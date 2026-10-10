"""Deterministic evaluator regressions; no provider or installed harness needed."""
import json
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import Future
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import run_eval as evaluator
from scripts import improve_description as improver
from scripts import run_loop as optimizer


class CompletedExecutor:
    outcomes = []

    def __init__(self, **kwargs):
        self.outcomes = iter(type(self).outcomes)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def submit(self, *args):
        future = Future()
        value = next(self.outcomes)
        if isinstance(value, Exception):
            future.set_exception(value)
        else:
            future.set_result(value)
        return future


class EvaluationTests(unittest.TestCase):
    def run_events(self, make_events):
        real_popen = subprocess.Popen
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def launch(*args, **kwargs):
                name = next((root / '.claude/commands').glob('*.md')).stem
                payload = ''.join(json.dumps(e) + '\n' for e in make_events(name))
                return real_popen([sys.executable, '-c', 'import sys; sys.stdout.write(sys.argv[1])', payload], stdout=subprocess.PIPE)

            with patch.object(evaluator.subprocess, 'Popen', side_effect=launch):
                result = evaluator.run_single_query('query', 'fixture', 'description', 2, directory)
            self.assertEqual(list((root / '.claude/commands').glob('*.md')), [])
            return result

    def test_read_before_target_in_full_message(self):
        self.assertTrue(self.run_events(lambda name: [
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'name': 'Read', 'input': {'file_path': '/project/AGENTS.md'}},
                {'type': 'tool_use', 'name': 'Skill', 'input': {'skill': name}},
            ]}}, {'type': 'result', 'is_error': False},
        ]))

    def test_other_tool_before_target_in_stream(self):
        def events(name):
            return [
                {'type': 'stream_event', 'event': {'type': 'content_block_start', 'content_block': {'type': 'tool_use', 'name': 'Bash'}}},
                {'type': 'stream_event', 'event': {'type': 'content_block_stop'}},
                {'type': 'stream_event', 'event': {'type': 'message_stop'}},
                {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Skill', 'input': {'skill': name}}]}},
                {'type': 'result', 'is_error': False},
            ]
        self.assertTrue(self.run_events(events))

    def test_completed_nonselection(self):
        self.assertFalse(self.run_events(lambda name: [{'type': 'result', 'is_error': False}]))

    def test_failed_or_incomplete_execution_is_not_nonselection(self):
        for events in ([{'type': 'result', 'is_error': True}], []):
            with self.subTest(events=events), self.assertRaises(RuntimeError):
                self.run_events(lambda name: events)

    def test_worker_failure_does_not_pass_negative_case(self):
        CompletedExecutor.outcomes = [FileNotFoundError('CLI unavailable')]
        with patch.object(evaluator, 'ProcessPoolExecutor', CompletedExecutor):
            result = evaluator.run_eval([{'query': 'near miss', 'should_trigger': False}], 'fixture', 'description', 1, 2, Path('.'))
        self.assertIsNone(result['results'][0]['pass'])
        self.assertIsNone(result['results'][0]['trigger_rate'])
        self.assertEqual(result['summary']['errors'], 1)
        self.assertEqual(result['summary']['passed'], 0)

    def test_partial_errors_are_unscored(self):
        CompletedExecutor.outcomes = [False, RuntimeError('timeout')]
        with patch.object(evaluator, 'ProcessPoolExecutor', CompletedExecutor):
            result = evaluator.run_eval([{'query': 'near miss', 'should_trigger': False}], 'fixture', 'description', 1, 2, Path('.'), runs_per_query=2)
        self.assertIsNone(result['results'][0]['pass'])
        self.assertEqual(result['results'][0]['runs'], 1)
        self.assertEqual(result['results'][0]['attempted_runs'], 2)

    def test_invalid_scores_do_not_reach_description_provider(self):
        result = {'results': [{'query': 'near miss', 'should_trigger': False, 'pass': None, 'errors': ['CLI unavailable'], 'triggers': 0, 'runs': 0}], 'summary': {'errors': 1, 'passed': 0, 'failed': 0, 'total': 1}}
        with patch.object(improver, '_call_llm') as provider:
            with self.assertRaises(ValueError):
                improver.improve_description('fixture', 'body', 'description', result, [], None)
            provider.assert_not_called()

    def test_invalid_scores_stop_optimization(self):
        result = {'results': [], 'summary': {'errors': 1}}
        with patch.object(optimizer, 'run_eval', return_value=result), patch.object(optimizer, 'improve_description') as improve:
            with self.assertRaises(RuntimeError):
                optimizer.run_loop([], Path(__file__).resolve().parents[1], None, 1, 2, 1, 1, 0.5, 0, 'fixture', False)
            improve.assert_not_called()


if __name__ == '__main__':
    unittest.main()
