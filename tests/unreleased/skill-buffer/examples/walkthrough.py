"""Synthetic offline CLI walkthrough, independent of the repository and cwd."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from buffer_core import inventory, read_json, write_json


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    before = {'baseline': inventory(ROOT / 'examples/baseline'), 'candidate': inventory(ROOT / 'examples/candidate')}
    def cli(*args):
        subprocess.run([sys.executable, '-B', str(ROOT / 'skill_buffer.py'), *map(str, args)], cwd=output, check=True)
    cli('inspect', '--input', ROOT / 'examples/baseline', '--output', output / 'inspection.json')
    cli('freeze', '--baseline', ROOT / 'examples/baseline', '--candidate', ROOT / 'examples/candidate', '--suite', ROOT / 'examples/suite.json', '--output', output / 'run')
    def assess(workspace, report):
        manifest = read_json(workspace / 'manifest.json')
        responses, grades = [], []
        for job in manifest['jobs']:
            case = next(c for c in manifest['suite']['cases'] if c['id'] == job['case_id'])
            response = '{"primary":"sample"}' if case['type'] == 'routing' else ('Check the parser; expect a passing fixture result.' if job['variant'] == 'candidate' else 'Check the parser.')
            responses.append({'job_id': job['id'], 'response': response, 'completion_status': 'complete', 'provenance': {'kind': 'synthetic-authored', 'cache_observation': 'unknown'}})
            if case['type'] == 'procedure':
                grades.append({'job_id': job['id'], 'case_id': case['id'], 'fingerprint': manifest['fingerprint'], 'response_sha256': hashlib.sha256(response.encode()).hexdigest(), 'assertion_results': [{'id': a['id'], 'text': a['text'], 'verdict': job['variant'] == 'candidate', 'evidence': [{'source': 'response', 'start': 0, 'end': len(response), 'quote': response}]} for a in case['assertions']]})
        write_json(workspace / 'responses-input.json', {'version': 1, 'attempts': responses})
        write_json(workspace / 'grades-input.json', {'version': 1, 'grades': grades})
        cli('import-responses', '--workspace', workspace, '--input', workspace / 'responses-input.json')
        cli('grade', '--workspace', workspace, '--input', workspace / 'grades-input.json', '--output', workspace / 'grades.json')
        cli('compare', '--workspace', workspace, '--input', workspace / 'grades.json', '--output', report)
    assess(output / 'run', output / 'report')
    cli('enhance', 'brief', '--workspace', output / 'run', '--input', output / 'run/grades.json', '--output', output / 'brief.json')
    shutil.copytree(ROOT / 'examples/candidate', output / 'authored-candidate')
    (output / 'authored-candidate/sample/guide.txt').write_text('Identify the target. State the expected fixture result and record observed evidence separately.\n')
    write_json(output / 'findings.json', {'version': 1, 'findings_addressed': ['procedure:0:baseline']})
    cli('enhance', 'record', '--workspace', output / 'run', '--candidate', output / 'authored-candidate', '--input', output / 'findings.json', '--output', output / 'enhanced')
    assess(output / 'enhanced', output / 'enhanced-report')
    after = {'baseline': inventory(ROOT / 'examples/baseline'), 'candidate': inventory(ROOT / 'examples/candidate')}
    if before != after:
        raise AssertionError('source changed')
    write_json(output / 'inventories.json', {'version': 1, 'before': before, 'after': after, 'limitation': 'Inventories detect persistent changes, not transient writes.'})
    write_json(output / 'summary.json', {'version': 1, 'synthetic': True, 'source_preserved': True, 'initial_matched_pairs': len(read_json(output / 'report/report.json')['matched_pairs']), 'enhanced_matched_pairs': len(read_json(output / 'enhanced-report/report.json')['matched_pairs']), 'limits': 'Authored response simulation; no inference, native activation or executed tasks.'})
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    run(parser.parse_args().output)
