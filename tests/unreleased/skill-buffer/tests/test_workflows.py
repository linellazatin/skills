import hashlib
import json
import os
from pathlib import Path
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_buffer import SkillFixture
from buffer_core import freeze, import_responses, read_json
from buffer_http import evaluate
from buffer_review import brief, compare, grade, record


class Workflows(SkillFixture):
    def response_rows(self, manifest, response='{"primary":"sample"}'):
        return {'version': 1, 'attempts': [{'job_id': j['id'], 'response': response, 'completion_status': 'complete', 'provenance': {}} for j in manifest['jobs']]}

    def server(self, mode='normal', fail_at=None):
        received = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass
            def do_POST(self):
                received.append(json.loads(self.rfile.read(int(self.headers['Content-Length']))))
                if mode == 'failure' or len(received) == fail_at:
                    self.send_error(503)
                    return
                if mode == 'timeout':
                    import time
                    time.sleep(0.1)
                self.send_response(200)
                self.end_headers()
                payload = {'choices': [{'message': {'content': '{"primary":"sample"}'}, 'finish_reason': 'length' if mode == 'truncated' else 'stop'}], 'echo': 'test-secret'}
                try:
                    self.wfile.write(b'broken' if mode == 'malformed' else json.dumps(payload).encode())
                except BrokenPipeError:
                    pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        return f'http://127.0.0.1:{server.server_port}/chat/completions', received

    def test_http_parameters_redaction_resume(self):
        manifest = self.frozen()
        endpoint, requests = self.server()
        os.environ['BUFFER_TEST_KEY'] = 'test-secret'
        self.addCleanup(os.environ.pop, 'BUFFER_TEST_KEY')
        result = evaluate(self.root / 'run', endpoint, 'synthetic', 'BUFFER_TEST_KEY')
        self.assertFalse(result['stopped'])
        self.assertEqual(requests[0]['temperature'], 0.6)
        self.assertEqual(requests[0]['seed'], 42)
        self.assertEqual(requests[0]['max_tokens'], 4096)
        self.assertNotIn('max_completion_tokens', requests[0])
        self.assertFalse(requests[0]['stream'])
        self.assertNotIn('test-secret', (self.root / 'run/attempts.json').read_text())
        self.assertIsNone(read_json(self.root / 'run/attempts.json')['attempts'][0]['telemetry'])
        evaluate(self.root / 'run', endpoint, 'synthetic', 'BUFFER_TEST_KEY', resume=True)
        self.assertEqual(len(requests), 2)
        with self.assertRaises(ValueError):
            evaluate(self.root / 'run', endpoint, 'changed', resume=True)

    def test_failure_and_explicit_resume(self):
        self.frozen()
        endpoint, requests = self.server('failure')
        self.assertTrue(evaluate(self.root / 'run', endpoint, 'test')['stopped'])
        self.assertEqual(len(requests), 1)
        self.assertEqual(read_json(self.root / 'run/attempts.json')['attempts'], [])
        self.assertEqual(read_json(self.root / 'run/failures.json')['failures'][0]['classification'], 'transport-error')
        self.assertTrue(evaluate(self.root / 'run', endpoint, 'test', resume=True)['stopped'])
        self.assertEqual(len(requests), 2)

    def test_resume_preserves_completed_attempt(self):
        self.frozen()
        endpoint, requests = self.server(fail_at=2)
        self.assertTrue(evaluate(self.root / 'run', endpoint, 'test')['stopped'])
        first = read_json(self.root / 'run/attempts.json')['attempts'][0]
        self.assertFalse(evaluate(self.root / 'run', endpoint, 'test', resume=True)['stopped'])
        self.assertEqual(read_json(self.root / 'run/attempts.json')['attempts'][0], first)
        self.assertEqual(len(requests), 3)

    def test_timeout(self):
        freeze(self.skill, self.skill, self.suite, self.root / 'run', {'timeout': 0.01})
        endpoint, _ = self.server('timeout')
        self.assertTrue(evaluate(self.root / 'run', endpoint, 'test')['stopped'])

    def test_http_malformed_and_truncated(self):
        for mode, expected in [('malformed', 'malformed-output'), ('truncated', 'truncated')]:
            workspace = self.root / mode
            freeze(self.skill, self.skill, self.suite, workspace)
            endpoint, _ = self.server(mode)
            evaluate(workspace, endpoint, 'test', token_field='max_completion_tokens')
            rows = read_json(workspace / 'attempts.json')['attempts']
            self.assertEqual(rows[0]['classification'], expected)
            self.assertNotIn('max_tokens', rows[0]['request'])
            self.assertEqual(rows[0]['request']['max_completion_tokens'], 4096)

    def test_routing_shapes_and_matched_pairs(self):
        for index, (response, completion, expected) in enumerate([('broken', 'complete', 'malformed-output'), ('{"primary":"sample","primary":"sample"}', 'complete', 'malformed-output'), ('[]', 'complete', 'invalid-output'), ('{"primary":"unknown"}', 'complete', 'invalid-output'), ('{"primary":"sample"}', 'truncated', 'truncated')]):
            workspace = self.root / f'run{index}'
            manifest = freeze(self.skill, self.skill, self.suite, workspace)
            rows = self.response_rows(manifest)
            rows['attempts'][0].update(response=response, completion_status=completion)
            data = import_responses(workspace, rows)
            self.assertEqual(data['attempts'][0]['classification'], expected)
            report = compare(workspace, {'version': 1, 'grades': []}, self.root / f'report{index}')
            self.assertEqual(report['matched_pairs'], [])

    def procedure(self):
        self.suite['cases'] += [{'id': 'proc', 'type': 'procedure', 'skill': 'sample', 'prompt': 'Do it', 'assertions': [{'id': 'proof', 'text': 'States proof', 'critical': True}]}, {'id': 'held', 'type': 'procedure', 'skill': 'sample', 'partition': 'acceptance', 'prompt': 'SECRET ACCEPTANCE', 'assertions': [{'id': 'proof', 'text': 'States proof', 'critical': True}]}]
        manifest = self.frozen()
        rows = self.response_rows(manifest)
        grades = []
        for row in rows['attempts']:
            if not row['job_id'].startswith('route:'):
                row['response'] = 'Check the parser.'
                grades.append({'job_id': row['job_id'], 'case_id': row['job_id'].split(':')[0], 'fingerprint': manifest['fingerprint'], 'response_sha256': hashlib.sha256(row['response'].encode()).hexdigest(), 'assertion_results': [{'id': 'proof', 'text': 'States proof', 'verdict': False, 'evidence': [{'source': 'response', 'start': 0, 'end': 5, 'quote': 'Check'}]}]})
        import_responses(self.root / 'run', rows)
        return manifest, {'version': 1, 'grades': grades}

    def test_grades_evidence_critical_and_brief(self):
        manifest, grades = self.procedure()
        grade(self.root / 'run', grades, self.root / 'grades.json')
        report = compare(self.root / 'run', grades, self.root / 'report')
        self.assertEqual(len(report['matched_pairs']), 3)
        self.assertEqual(report['results']['proc:0:baseline']['critical_failures'], ['proof'])
        exported = brief(self.root / 'run', grades, self.root / 'brief.json')
        self.assertNotIn('SECRET ACCEPTANCE', json.dumps(exported))
        self.assertEqual(len(exported['failures']), 2)
        grades['grades'][0]['assertion_results'][0]['evidence'][0]['end'] = 999
        with self.assertRaises(ValueError):
            grade(self.root / 'run', grades, self.root / 'bad.json')

    def test_missing_duplicate_grades(self):
        _, grades = self.procedure()
        report = compare(self.root / 'run', {'version': 1, 'grades': []}, self.root / 'report')
        self.assertEqual(len(report['missing']), 4)
        grades['grades'].append(grades['grades'][0])
        with self.assertRaises(ValueError):
            grade(self.root / 'run', grades, self.root / 'bad.json')

    def test_enhancement_resource_diff_and_preservation(self):
        manifest, grades = self.procedure()
        before = (self.skill / 'SKILL.md').read_bytes()
        candidate = self.root / 'new/sample'
        import shutil
        shutil.copytree(self.skill, candidate)
        (candidate / 'guide.txt').write_text('State evidence.')
        result = record(self.root / 'run', candidate, {'version': 1, 'findings_addressed': ['proc:0:baseline']}, self.root / 'enhanced')
        self.assertEqual(result['changes'][0]['path'], 'sample/guide.txt')
        self.assertEqual((self.skill / 'SKILL.md').read_bytes(), before)
        self.assertEqual(len(read_json(self.root / 'enhanced/manifest.json')['suite']['cases']), 2)

    def test_valid_wrong_routing_and_alternating_order(self):
        other = self.root / 'other'
        other.mkdir()
        (other / 'SKILL.md').write_text('---\nname: other\ndescription: Another skill.\n---\n')
        collection = self.root / 'collection'
        import shutil
        shutil.copytree(self.skill, collection / 'sample')
        shutil.copytree(other, collection / 'other')
        manifest = freeze(collection, collection, self.suite, self.root / 'run', {'repeats': 2})
        self.assertEqual([j['variant'] for j in manifest['jobs']], ['baseline', 'candidate', 'candidate', 'baseline'])
        rows = self.response_rows(manifest, '{"primary":"other"}')
        data = import_responses(self.root / 'run', rows)
        self.assertTrue(all(a['classification'] == 'valid' for a in data['attempts']))
        report = compare(self.root / 'run', {'version': 1, 'grades': []}, self.root / 'report')
        self.assertEqual(len(report['matched_pairs']), 2)
        self.assertTrue(all(p['baseline']['score'] == 0 for p in report['matched_pairs']))

    def test_metadata_escaping_links_and_settings(self):
        (self.skill / 'SKILL.md').write_text('---\nname: sample\ndescription: x\nmetadata: invalid\n---\n')
        from buffer_core import inspect
        self.assertTrue(inspect(self.skill)['structural_findings'])
        (self.skill / 'SKILL.md').write_text('---\nname: sample\ndescription: x\n---\n[x](../outside.txt)')
        self.assertTrue(inspect(self.skill)['structural_findings'])
        with self.assertRaises(ValueError):
            freeze(self.skill, self.skill, self.suite, self.root / 'bad', {'provider_parameters': {'max_completion_tokens': 99}})

    def test_assertion_coverage_and_grade_identity(self):
        _, grades = self.procedure()
        original = json.loads(json.dumps(grades))
        for key, value in [('response_sha256', 'bad'), ('case_id', 'wrong'), ('fingerprint', 'wrong'), ('assertion_results', [])]:
            changed = json.loads(json.dumps(original))
            changed['grades'][0][key] = value
            with self.assertRaises(ValueError):
                grade(self.root / 'run', changed, self.root / 'bad.json')

    def test_copied_cli_walkthrough(self):
        import shutil
        import subprocess
        prototype = self.root / 'prototype'
        shutil.copytree(Path(__file__).resolve().parents[1], prototype, ignore=shutil.ignore_patterns('__pycache__', '.venv', 'runs'))
        subprocess.run([sys.executable, '-B', str(prototype / 'examples/walkthrough.py'), '--output', str(self.root / 'walkthrough')], cwd=self.root, check=True, capture_output=True, text=True)
        self.assertTrue(read_json(self.root / 'walkthrough/summary.json')['source_preserved'])

    def test_license_retention_before_output_creation(self):
        (self.skill / 'LICENSE').write_text('Retained notice')
        self.procedure()
        import shutil
        candidate = self.root / 'authored/sample'
        shutil.copytree(self.skill, candidate)
        (candidate / 'LICENSE').write_text('Changed notice')
        with self.assertRaises(ValueError):
            record(self.root / 'run', candidate, {'version': 1, 'findings_addressed': ['proc:0:baseline']}, self.root / 'rejected')
        self.assertFalse((self.root / 'rejected').exists())

    def test_import_batch_atomic_and_cache_provenance(self):
        manifest = self.frozen()
        rows = self.response_rows(manifest)
        rows['attempts'][1]['job_id'] = rows['attempts'][0]['job_id']
        with self.assertRaises(ValueError):
            import_responses(self.root / 'run', rows)
        self.assertEqual(read_json(self.root / 'run/attempts.json')['attempts'], [])
        rows = self.response_rows(manifest)
        rows['attempts'][0]['provenance'] = {'cache_hit': True}
        result = import_responses(self.root / 'run', rows)
        self.assertTrue(result['attempts'][0]['provenance']['supplied']['cache_hit'])

    def test_provider_credentials_rejected(self):
        with self.assertRaises(ValueError):
            freeze(self.skill, self.skill, self.suite, self.root / 'bad', {'provider_parameters': {'nested': {'Authorization': 'secret'}}})


if __name__ == '__main__':
    unittest.main()
