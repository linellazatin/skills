import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = load("release_notes")
validator = load("validate_skills")


class ReleaseNotesTests(unittest.TestCase):
    def test_exact_version_and_subsections(self):
        for heading in ("Added", "New"):
            with self.subTest(heading=heading):
                doc = f"## 0.20.0\nwrong\n## 0.2.0\n\n### {heading}\n- right\n## 0.1.0\nold"
                self.assertEqual(release.extract_notes(doc, "v0.2.0"), f"### {heading}\n- right\n")

    def test_brackets_date_and_prerelease(self):
        doc = "## [1.2.3-rc.1] - 2026-10-11\n- preview\n## [1.2.2]\nold"
        self.assertEqual(release.extract_notes(doc, "v1.2.3-rc.1"), "- preview\n")

    def test_missing_duplicate_and_empty_sections_fail(self):
        for doc in ("## 1.0.0\nother", "## 0.2.0\na\n## [0.2.0]\nb", "## 0.2.0\n\n## 0.1.0\nold"):
            with self.subTest(doc=doc), self.assertRaises(ValueError):
                release.extract_notes(doc, "v0.2.0")

    def test_invalid_tags_fail(self):
        for tag in ("0.2.0", "vgarbage", "v01.2.3", "v1.2.3-01", "v1.2.3-rc..1"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                release.extract_notes("## 0.2.0\nnotes", tag)

    def test_fenced_headings_are_content(self):
        doc = "## 0.2.0\n```markdown\n## 0.1.0\n```\n- retained\n## 0.1.0\nold"
        self.assertIn("- retained", release.extract_notes(doc, "v0.2.0"))


class FrontmatterTests(unittest.TestCase):
    def check(self, content):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "example"
            skill.mkdir()
            if content is not None:
                (skill / "SKILL.md").write_text(content)
            return validator.validate_all(root)

    def test_valid_skill_and_collection(self):
        self.assertEqual(self.check("---\nname: example\ndescription: Example skill\n---\nBody"), [])
        self.assertEqual(validator.validate_all(), [])

    def test_malformed_yaml(self):
        self.assertTrue(self.check("---\nname: example\ndescription: [broken\n---\nBody"))

    def test_duplicate_keys(self):
        for extra in ("name: example", "metadata:\n  mode: one\n  mode: two"):
            self.assertTrue(self.check(f"---\nname: example\ndescription: Example\n{extra}\n---\nBody"))

    def test_nonstring_description(self):
        self.assertTrue(self.check("---\nname: example\ndescription: false\n---\nBody"))

    def test_directory_contract_and_missing_entrypoint(self):
        self.assertTrue(self.check("---\nname: other\ndescription: Example\n---\nBody"))
        self.assertTrue(self.check(None))

    def test_empty_collection(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(validator.validate_all(Path(directory)))


if __name__ == "__main__":
    unittest.main()
