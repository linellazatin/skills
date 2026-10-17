"""Evidence-location checks, author grading, paired comparisons and revision handoff."""
import difflib
import hashlib
import json
from pathlib import Path

from buffer_core import attempt_store, freeze, inspect, inventory, load_workspace, read_json, version, write_json


LIMITATIONS = ['Semantic grading is author review; evidence-location validation does not validate judgment.', 'Response simulations show proposed decisions, not executed tasks, absence of writes, native activation or host readiness.', 'Missing telemetry and cache observations remain unknown; imports do not prove fresh inference.']


def validate_grades(manifest, attempts, payload):
    version(payload)
    if not isinstance(payload.get('grades'), list):
        raise ValueError('grades must be a list')
    by_job = {a['job_id']: a for a in attempts}
    jobs = {j['id']: j for j in manifest['jobs']}
    cases = {c['id']: c for c in manifest['suite']['cases']}
    seen = set()
    for grade in payload['grades']:
        if not isinstance(grade, dict) or not isinstance(grade.get('job_id'), str):
            raise ValueError('grade must identify a job')
        jid = grade.get('job_id')
        if jid not in by_job or jid in seen or by_job[jid]['classification'] != 'valid':
            raise ValueError('unknown, duplicate or invalid graded attempt')
        seen.add(jid)
        case = cases[jobs[jid]['case_id']]
        if case['type'] != 'procedure' or grade.get('case_id') != case['id'] or grade.get('fingerprint') != manifest['fingerprint'] or grade.get('response_sha256') != hashlib.sha256(by_job[jid]['response'].encode()).hexdigest():
            raise ValueError('grade identity mismatch')
        expected = {a['id']: a for a in case['assertions']}
        results = grade.get('assertion_results')
        if not isinstance(results, list) or len(results) != len(expected) or any(not isinstance(a, dict) or not isinstance(a.get('id'), str) for a in results) or {a.get('id') for a in results} != set(expected):
            raise ValueError('assertion coverage mismatch')
        for result in results:
            if result.get('text') != expected[result['id']]['text'] or type(result.get('verdict')) is not bool or not isinstance(result.get('evidence'), list) or not result['evidence']:
                raise ValueError('assertion text, Boolean verdict and evidence required')
            for evidence in result['evidence']:
                if not isinstance(evidence, dict):
                    raise ValueError('evidence must be an object')
                start, end = evidence.get('start'), evidence.get('end')
                response = by_job[jid]['response']
                if evidence.get('source') != 'response' or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(response) or evidence.get('quote') != response[start:end]:
                    raise ValueError('invalid evidence location or quote')
    return payload


def grade(workspace, payload, output):
    manifest = load_workspace(workspace)
    attempts = attempt_store(workspace, manifest)['attempts']
    validated = validate_grades(manifest, attempts, payload)
    write_json(output, validated)
    return {'version': 1, 'validated_grades': len(validated['grades']), 'semantic_review': 'author review'}


def compare(workspace, grades, output):
    manifest = load_workspace(workspace)
    attempts = attempt_store(workspace, manifest)['attempts']
    grades = validate_grades(manifest, attempts, grades)
    judgments = {g['job_id']: g for g in grades['grades']}
    by_job = {a['job_id']: a for a in attempts}
    results, missing, invalid = {}, [], []
    for job in manifest['jobs']:
        case = next(c for c in manifest['suite']['cases'] if c['id'] == job['case_id'])
        attempt = by_job.get(job['id'])
        if not attempt:
            missing.append({'job_id': job['id'], 'reason': 'missing attempt'})
            continue
        if attempt['classification'] != 'valid':
            invalid.append({'job_id': job['id'], 'classification': attempt['classification']})
            continue
        critical = []
        if case['type'] == 'routing':
            passed = json.loads(attempt['response'])['primary'] in case['acceptable_primary']
            score = int(passed)
            critical = [a['id'] for a in case['assertions'] if a.get('critical') and not passed]
        else:
            if job['id'] not in judgments:
                missing.append({'job_id': job['id'], 'reason': 'missing author grade'})
                continue
            assertions = judgments[job['id']]['assertion_results']
            critical_ids = {a['id'] for a in case['assertions'] if a.get('critical')}
            critical = [a['id'] for a in assertions if a['id'] in critical_ids and not a['verdict']]
            score = sum(a['verdict'] for a in assertions) / len(assertions)
            passed = score == 1 and not critical
        results[job['id']] = {'score': score, 'passed': passed, 'critical_failures': critical}
    pairs = []
    for case in manifest['suite']['cases']:
        for repeat in range(manifest['settings']['repeats']):
            ids = [f'{case["id"]}:{repeat}:{v}' for v in ('baseline', 'candidate')]
            if all(j in results for j in ids):
                pairs.append({'case_id': case['id'], 'partition': case.get('partition', 'development'), 'repeat': repeat, 'baseline': results[ids[0]], 'candidate': results[ids[1]], 'delta': results[ids[1]]['score'] - results[ids[0]]['score']})
    report = {'version': 1, 'fingerprint': manifest['fingerprint'], 'results': results, 'matched_pairs': pairs, 'invalid_attempts': invalid, 'missing': missing, 'telemetry': {a['job_id']: a.get('telemetry') for a in attempts}, 'provenance': {a['job_id']: a['provenance'] for a in attempts}, 'transport_failures': read_json(Path(workspace) / 'failures.json')['failures'] if (Path(workspace) / 'failures.json').exists() else [], 'limitations': LIMITATIONS}
    output = Path(output)
    if output.exists():
        raise ValueError('report output must be new')
    output.mkdir(parents=True)
    write_json(output / 'report.json', report)
    lines = ['# Skill Buffer comparison', '', f'Valid matched pairs: {len(pairs)}. Invalid attempts: {len(invalid)}. Missing: {len(missing)}.', '', '| Case | Repeat | Baseline | Candidate | Delta |', '| --- | --- | --- | --- | --- |']
    lines.extend(f'| {p["case_id"]} | {p["repeat"]} | {p["baseline"]["score"]:.2f} | {p["candidate"]["score"]:.2f} | {p["delta"]:+.2f} |' for p in pairs)
    lines += ['', '## Critical failures', ''] + [f'- {jid}: {", ".join(r["critical_failures"])}' for jid, r in results.items() if r['critical_failures']]
    lines += ['', '## Invalid and missing', '', json.dumps({'invalid': invalid, 'missing': missing}), '', '## Telemetry', '', json.dumps(report['telemetry']), '', '## Provenance', '', json.dumps(report['provenance']), '', f'Transport failures: {len(report["transport_failures"])}.', '', '## Limits', ''] + ['- ' + x for x in LIMITATIONS]
    (output / 'report.md').write_text('\n'.join(lines) + '\n')
    return report


def brief(workspace, grades, output):
    manifest = load_workspace(workspace)
    attempts = attempt_store(workspace, manifest)['attempts']
    validate_grades(manifest, attempts, grades)
    judgments = {g['job_id']: g for g in grades['grades']}
    jobs = {j['id']: j for j in manifest['jobs']}
    failures = []
    for attempt in attempts:
        job = jobs[attempt['job_id']]
        case = next(c for c in manifest['suite']['cases'] if c['id'] == job['case_id'])
        if case.get('partition') == 'acceptance' or attempt['classification'] != 'valid':
            continue
        failed = (json.loads(attempt['response'])['primary'] not in case['acceptable_primary']) if case['type'] == 'routing' else any(not r['verdict'] for r in judgments.get(job['id'], {}).get('assertion_results', []))
        if failed:
            failures.append({'finding_id': job['id'], 'case': case, 'quoted_response': attempt['response'], 'assertion_results': judgments.get(job['id'], {}).get('assertion_results'), 'relevant_instructions': job['prompt']})
    result = {'version': 1, 'fingerprint': manifest['fingerprint'], 'failures': failures, 'constraints': ['Author revisions inline in a separate candidate directory.', 'Preserve licenses and resource links; never apply edits to source skills.', 'Reuse frozen development cases; exclude acceptance cases from revision briefs.'], 'limitations': LIMITATIONS}
    write_json(output, result)
    return result


def record(workspace, candidate, findings, output):
    manifest = load_workspace(workspace)
    version(findings)
    addressed = findings.get('findings_addressed')
    if not isinstance(addressed, list) or not addressed or any(not isinstance(x, str) for x in addressed) or len(set(addressed)) != len(addressed):
        raise ValueError('unique findings_addressed required')
    jobs = {j['id']: j for j in manifest['jobs']}
    development = {c['id'] for c in manifest['suite']['cases'] if c.get('partition') != 'acceptance'}
    if any(x not in jobs or jobs[x]['case_id'] not in development for x in addressed):
        raise ValueError('findings must refer to frozen development jobs')
    if inspect(candidate)['structural_findings']:
        raise ValueError('candidate structural validation failed')
    candidate = Path(candidate).resolve()
    workspace = Path(workspace).resolve()
    if candidate.is_relative_to(workspace) or workspace.is_relative_to(candidate):
        raise ValueError('candidate must be separate from workspace')
    from buffer_core import skill_dirs
    proposed = {}
    for folder in skill_dirs(candidate):
        proposed.update({folder.name + '/' + name: hash_value for name, hash_value in inventory(folder).items()})
    for name, hash_value in inventory(workspace / 'snapshots/candidate').items():
        if Path(name).name.upper().startswith(('LICENSE', 'NOTICE')) and proposed.get(name) != hash_value:
            raise ValueError('retained license/notice must not change or disappear')
    # Freeze the candidate with exactly the existing development cases/settings.
    suite = {'version': 1, 'cases': [c for c in manifest['suite']['cases'] if c['id'] in development]}
    new = freeze(workspace / 'snapshots/baseline', candidate, suite, output, manifest['settings'])
    oldroot = workspace / 'snapshots/candidate'
    newroot = Path(output) / 'snapshots/candidate'
    old, current = inventory(oldroot), inventory(newroot)
    changes = []
    for name in sorted(set(old) | set(current)):
        if old.get(name) == current.get(name):
            continue
        before = (oldroot / name).read_bytes() if name in old else b''
        after = (newroot / name).read_bytes() if name in current else b''
        try:
            diff = ''.join(difflib.unified_diff(before.decode().splitlines(True), after.decode().splitlines(True), fromfile='before/' + name, tofile='after/' + name))
        except UnicodeDecodeError:
            diff = 'binary resource changed'
        changes.append({'path': name, 'before_sha256': old.get(name), 'after_sha256': current.get(name), 'diff': diff})
    result = {'version': 1, 'parent_fingerprint': manifest['fingerprint'], 'fingerprint': new['fingerprint'], 'findings_addressed': addressed, 'changes': changes, 'semantic_review': 'author revision; addressed claims not semantically verified'}
    write_json(Path(output) / 'enhancement.json', result)
    return result
