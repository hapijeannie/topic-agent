import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALID = '---\ntitle: 标题\nslug: test\n---\n原文内容\n'


class PreviewTests(unittest.TestCase):
    def run_cli(self, directory):
        return subprocess.run(
            [sys.executable, '-m', 'topic_agent.preview', str(directory),
             '--source', 'blog', '--ownership', 'owned'],
            cwd=ROOT, capture_output=True, text=True,
        )

    def test_reports_bad_file_and_continues_without_changing_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            good = directory / 'good.md'
            bad = directory / 'bad.md'
            good.write_text(VALID)
            bad.write_text('no metadata')
            before = {p.name: p.read_bytes() for p in directory.iterdir()}
            result = self.run_cli(directory)
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report['counts']['ready'], 1)
            self.assertEqual(report['counts']['error'], 1)
            self.assertNotIn('原文内容', result.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in directory.iterdir()})

    def test_marks_identical_duplicate_but_rejects_conflicting_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'a.md').write_text(VALID)
            (directory / 'b.md').write_text(VALID)
            result = self.run_cli(directory)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)['counts']['duplicate'], 1)
            (directory / 'c.md').write_text(VALID.replace('原文内容', '修改后的正文'))
            result = self.run_cli(directory)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['counts']['conflict'], 1)

    def test_rejects_empty_directory_and_missing_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            for path in [Path(tmp), Path(tmp) / 'missing']:
                with self.subTest(path=path):
                    result = self.run_cli(path)
                    self.assertEqual(result.returncode, 1)
                    self.assertIn('error', json.loads(result.stdout))

    def test_invalid_utf8_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'bad.md').write_bytes(b'\xff\xfe')
            result = self.run_cli(tmp)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['counts']['error'], 1)


if __name__ == '__main__':
    unittest.main()
