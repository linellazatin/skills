import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from buffer_core import inspect, freeze, load_workspace, import_responses


class SkillFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / 'sample'
        self.skill.mkdir()
        (self.skill / 'SKILL.md').write_text('---\nname: sample\ndescription: |\n  A sample skill.\n---\nRead [resource](guide.txt).\n')
        (self.skill / 'guide.txt').write_text('original')
        self.suite = {'version': 1, 'cases': [{'id': 'route', 'type': 'routing', 'prompt': 'choose', 'acceptable_primary': ['sample'], 'assertions': []}]}

    def frozen(self):
        return freeze(self.skill, self.skill, self.suite, self.root / 'run')


class Foundation(SkillFixture):

    def test_inspection_and_snapshot(self):
        self.assertEqual(inspect(self.skill)['structural_findings'], [])
        self.frozen()
        (self.skill / 'guide.txt').write_text('changed')
        self.assertEqual((self.root / 'run/snapshots/baseline/sample/guide.txt').read_text(), 'original')
        load_workspace(self.root / 'run')

    def test_duplicate_yaml_and_missing_link(self):
        (self.skill / 'SKILL.md').write_text('---\nname: sample\nname: other\ndescription: x\n---\n')
        self.assertTrue(inspect(self.skill)['structural_findings'])
        (self.skill / 'SKILL.md').write_text('---\nname: sample\ndescription: x\n---\n[x](missing)')
        self.assertTrue(inspect(self.skill)['structural_findings'])

    def test_overlap_and_symlink(self):
        with self.assertRaises(ValueError):
            freeze(self.skill, self.skill, self.suite, self.skill / 'run')
        (self.skill / 'escape').symlink_to(self.root)
        self.assertTrue(inspect(self.skill)['structural_findings'])

    def test_import_identity_duplicate_and_tamper(self):
        manifest = self.frozen()
        row = {'job_id': manifest['jobs'][0]['id'], 'response': '{"primary":"sample"}', 'completion_status': 'complete', 'provenance': {}}
        import_responses(self.root / 'run', {'version': 1, 'attempts': [row]})
        with self.assertRaises(ValueError):
            import_responses(self.root / 'run', {'version': 1, 'attempts': [row]})
        row['job_id'] = 'unknown'
        with self.assertRaises(ValueError):
            import_responses(self.root / 'run', {'version': 1, 'attempts': [row]})
        (self.root / 'run/snapshots/baseline/sample/guide.txt').write_text('tampered')
        with self.assertRaises(ValueError):
            load_workspace(self.root / 'run')


if __name__ == '__main__':
    unittest.main()
