"""Frozen, portable skill assessment contracts. No source writes or script execution."""
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import yaml


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def parse_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f'invalid JSON constant: {value}')))


def read_json(path):
    return parse_json(Path(path).read_text())


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()


def version(data):
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('expected version 1 object')


def inside(root, relative):
    root = Path(root).resolve()
    if Path(relative).is_absolute() or not (root / relative).resolve().is_relative_to(root):
        raise ValueError(f'escaping resource: {relative}')
    return root / relative


def inventory(root):
    root = Path(root).resolve()
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            # Refuse even internal symlinks: snapshots must be relocatable and acyclic.
            raise ValueError(f'symlink not supported: {path.relative_to(root)}')
        if path.is_file():
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def skill_dirs(root):
    root = Path(root)
    if (root / 'SKILL.md').is_file():
        return [root]
    return sorted(p for p in root.iterdir() if p.is_dir())


def inspect(root):
    findings, catalog = [], []
    try:
        inventory(root)
        folders = skill_dirs(root)
        if not folders:
            raise ValueError('no immediate skill directories')
        for folder in folders:
            try:
                text = (folder / 'SKILL.md').read_text()
                lines = text.splitlines()
                if not lines or lines[0] != '---':
                    raise ValueError('missing frontmatter')
                end = lines.index('---', 1)
                fields = yaml.load('\n'.join(lines[1:end]), Loader=UniqueLoader)
                if not isinstance(fields, dict):
                    raise ValueError('frontmatter must be a mapping')
                for key in ('name', 'description'):
                    if not isinstance(fields.get(key), str) or not fields[key].strip():
                        raise ValueError(f'invalid {key}')
                if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', fields['name']) or fields['name'] != folder.name:
                    raise ValueError('name must match directory and use lowercase hyphenated words')
                if 'metadata' in fields and not isinstance(fields['metadata'], dict):
                    raise ValueError('metadata must be a mapping')
                for document in folder.rglob('*.md'):
                    for link in re.findall(r'\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)', document.read_text()):
                        if re.match(r'^[a-zA-Z][\w+.-]*:', link) or link.startswith('#'):
                            continue
                        target = link.split('#')[0]
                        path = inside(folder, str(document.parent.relative_to(folder) / target))
                        if not path.exists():
                            raise ValueError(f'missing resource: {target}')
                catalog.append({'name': fields['name'], 'description': fields['description'], 'directory': folder.name})
            except (OSError, ValueError, TypeError, yaml.YAMLError) as error:
                findings.append({'id': f'structure-{folder.name}', 'skill': folder.name, 'message': str(error)})
    except (OSError, ValueError) as error:
        findings.append({'id': 'structure-tree', 'message': str(error)})
    return {'version': 1, 'catalog': catalog, 'structural_findings': findings, 'semantic_review': 'not performed'}


DEFAULT_SETTINGS = {'temperature': 0.6, 'seed': 42, 'max_tokens': 4096, 'repeats': 1, 'timeout': 300, 'provider_parameters': {}}
ROUTING_TEMPLATE = 'Choose the primary skill for the prompt. Return only JSON with a primary string from the catalog.\nCatalog:\n{catalog}\nPrompt:\n{prompt}'
PROCEDURE_TEMPLATE = 'Propose how you would handle the prompt using these instructions. This is a response simulation, not execution.\n{instructions}\nSelected resources:\n{resources}\nPrompt:\n{prompt}\nFixture:\n{fixture}'


def validate_settings(settings):
    if set(settings) != set(DEFAULT_SETTINGS):
        raise ValueError('unsupported run settings')
    for key in ('temperature', 'timeout'):
        if type(settings[key]) not in (int, float) or not math.isfinite(settings[key]) or settings[key] < 0:
            raise ValueError(f'invalid {key}')
    if settings['timeout'] == 0:
        raise ValueError('timeout must be positive')
    for key in ('seed', 'max_tokens', 'repeats'):
        if type(settings[key]) is not int or (key != 'seed' and settings[key] < 1):
            raise ValueError(f'invalid {key}')
    params = settings['provider_parameters']
    if not isinstance(params, dict) or any(k in params for k in ('model', 'messages', 'stream', 'temperature', 'seed', 'max_tokens', 'max_completion_tokens', 'api_key', 'authorization')):
        raise ValueError('provider parameters must not override core fields or token caps/credentials')
    def no_credentials(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key.lower().replace('-', '_') in ('api_key', 'authorization', 'password', 'secret', 'access_token', 'headers', 'credentials'):
                    raise ValueError('credentials must not enter provider parameters')
                no_credentials(item)
        elif isinstance(value, list):
            for item in value:
                no_credentials(item)
    no_credentials(params)


def validate_suite(suite, catalogs, roots):
    version(suite)
    if not isinstance(suite.get('cases'), list) or not suite['cases']:
        raise ValueError('cases must be a nonempty list')
    ids = set()
    for case in suite['cases']:
        if not isinstance(case, dict) or not isinstance(case.get('id'), str) or not re.fullmatch(r'[\w-]+', case['id']) or case['id'] in ids:
            raise ValueError('invalid or duplicate case ID')
        ids.add(case['id'])
        if not isinstance(case.get('prompt'), str) or not case['prompt'].strip() or case.get('type') not in ('routing', 'procedure'):
            raise ValueError('invalid case prompt/type')
        if case.get('partition', 'development') not in ('development', 'acceptance'):
            raise ValueError('invalid partition')
        assertions = case.get('assertions')
        if not isinstance(assertions, list):
            raise ValueError('assertions must be a list')
        aids = set()
        for assertion in assertions:
            if not isinstance(assertion, dict) or not isinstance(assertion.get('id'), str) or not assertion['id'].strip() or assertion['id'] in aids or not isinstance(assertion.get('text'), str) or not assertion['text'].strip() or type(assertion.get('critical', False)) is not bool:
                raise ValueError('invalid or duplicate assertion')
            aids.add(assertion['id'])
        for variant, catalog in catalogs.items():
            names = {item['name'] for item in catalog}
            if case['type'] == 'routing':
                choices = case.get('acceptable_primary')
                if not isinstance(choices, list) or not choices or any(not isinstance(x, str) or x not in names for x in choices):
                    raise ValueError('acceptable primary choices must exist in both catalogs')
            else:
                if case.get('skill') not in names or not assertions:
                    raise ValueError('procedure needs a known skill and assertions')
                resources = case.get('resources', [])
                if not isinstance(resources, list) or any(not isinstance(x, str) for x in resources):
                    raise ValueError('resources must be explicit relative paths')
                for relative in resources:
                    inside(roots[variant] / case['skill'], relative).read_text()


def freeze(baseline, candidate, suite, output, settings=None):
    roots = {'baseline': Path(baseline).resolve(), 'candidate': Path(candidate).resolve()}
    output = Path(output).resolve()
    for root in roots.values():
        if root.is_relative_to(output) or output.is_relative_to(root):
            raise ValueError('overlapping input/output trees')
    if output.exists():
        raise ValueError('output workspace must be new')
    settings = dict(DEFAULT_SETTINGS, **(settings or {}))
    validate_settings(settings)
    reports = {key: inspect(root) for key, root in roots.items()}
    if any(r['structural_findings'] for r in reports.values()):
        raise ValueError('structural inspection failed: ' + json.dumps(reports))
    catalogs = {k: v['catalog'] for k, v in reports.items()}
    # Normalize single-skill inputs to collection roots in the new workspace.
    for variant, root in roots.items():
        for folder in skill_dirs(root):
            inventory(folder)
    normalized = {k: (r.parent if (r / 'SKILL.md').is_file() else r) for k, r in roots.items()}
    validate_suite(suite, catalogs, normalized)
    output.mkdir(parents=True)
    for variant, root in roots.items():
        for folder in skill_dirs(root):
            shutil.copytree(folder, output / 'snapshots' / variant / folder.name)
    jobs = []
    for index, case in enumerate(suite['cases']):
        for repeat in range(settings['repeats']):
            order = ('baseline', 'candidate') if (index * settings['repeats'] + repeat) % 2 == 0 else ('candidate', 'baseline')
            for variant in order:
                if case['type'] == 'routing':
                    prompt = ROUTING_TEMPLATE.format(catalog=json.dumps([{'name': x['name'], 'description': x['description']} for x in catalogs[variant]]), prompt=case['prompt'])
                else:
                    skill = output / 'snapshots' / variant / case['skill']
                    prompt = PROCEDURE_TEMPLATE.format(instructions=(skill / 'SKILL.md').read_text(), resources=json.dumps({p: inside(skill, p).read_text() for p in case.get('resources', [])}), prompt=case['prompt'], fixture=json.dumps(case.get('fixture')))
                jobs.append({'id': f'{case["id"]}:{repeat}:{variant}', 'case_id': case['id'], 'repeat': repeat, 'variant': variant, 'prompt': prompt})
    manifest = {'version': 1, 'suite': suite, 'catalogs': catalogs, 'settings': settings, 'templates': {'routing': ROUTING_TEMPLATE, 'procedure': PROCEDURE_TEMPLATE}, 'jobs': jobs, 'resources': inventory(output / 'snapshots')}
    manifest['fingerprint'] = digest(manifest)
    write_json(output / 'manifest.json', manifest)
    write_json(output / 'attempts.json', {'version': 1, 'attempts': []})
    return manifest


def load_workspace(workspace):
    workspace = Path(workspace)
    manifest = read_json(workspace / 'manifest.json')
    version(manifest)
    original = dict(manifest)
    fingerprint = original.pop('fingerprint')
    if digest(original) != fingerprint or inventory(workspace / 'snapshots') != manifest['resources']:
        raise ValueError('frozen-input mismatch')
    return manifest


def classify(manifest, job, response, completion):
    if completion == 'transport-error':
        return 'transport-error'
    if completion == 'truncated':
        return 'truncated'
    if completion == 'malformed-output':
        return 'malformed-output'
    case = next(c for c in manifest['suite']['cases'] if c['id'] == job['case_id'])
    if not response.strip():
        return 'invalid-output'
    if case['type'] == 'routing':
        try:
            answer = parse_json(response)
        except (ValueError, TypeError):
            return 'malformed-output'
        if not isinstance(answer, dict) or set(answer) != {'primary'} or not isinstance(answer['primary'], str) or answer['primary'] not in {x['name'] for x in manifest['catalogs'][job['variant']]}:
            return 'invalid-output'
    return 'valid'


def attempt_store(workspace, manifest):
    data = read_json(Path(workspace) / 'attempts.json')
    version(data)
    if not isinstance(data.get('attempts'), list):
        raise ValueError('stored attempts must be a list')
    ids = set()
    jobs = {j['id']: j for j in manifest['jobs']}
    for row in data['attempts']:
        if not isinstance(row, dict) or not isinstance(row.get('job_id'), str) or not isinstance(row.get('response'), str) or row.get('completion_status') not in ('complete', 'truncated', 'transport-error', 'malformed-output') or not isinstance(row.get('provenance'), dict):
            raise ValueError('invalid stored attempt shape')
        if row['job_id'] not in jobs or row['job_id'] in ids or row.get('fingerprint') != manifest['fingerprint'] or row.get('classification') != classify(manifest, jobs[row['job_id']], row['response'], row['completion_status']):
            raise ValueError('invalid attempt identity/classification')
        ids.add(row['job_id'])
    return data


def import_responses(workspace, payload):
    manifest = load_workspace(workspace)
    data = attempt_store(workspace, manifest)
    version(payload)
    if not isinstance(payload.get('attempts'), list):
        raise ValueError('attempts must be a list')
    jobs = {j['id']: j for j in manifest['jobs']}
    seen = {a['job_id'] for a in data['attempts']}
    additions = []
    for row in payload['attempts']:
        if not isinstance(row, dict) or not isinstance(row.get('job_id'), str):
            raise ValueError('attempt must identify a job')
        if row.get('job_id') not in jobs or row['job_id'] in seen:
            raise ValueError('unknown job or duplicate attempt')
        if not isinstance(row.get('response'), str) or row.get('completion_status') not in ('complete', 'truncated', 'transport-error') or not isinstance(row.get('provenance'), dict):
            raise ValueError('response, completion status and provenance required')
        if row.get('telemetry') is not None and not isinstance(row['telemetry'], dict):
            raise ValueError('telemetry must be an object or null')
        seen.add(row['job_id'])
        additions.append({'job_id': row['job_id'], 'response': row['response'], 'completion_status': row['completion_status'], 'provenance': {'label': 'external-import', 'supplied': row['provenance']}, 'telemetry': row.get('telemetry'), 'fingerprint': manifest['fingerprint'], 'classification': classify(manifest, jobs[row['job_id']], row['response'], row['completion_status'])})
    data['attempts'].extend(additions)
    write_json(Path(workspace) / 'attempts.json', data)
    return data
