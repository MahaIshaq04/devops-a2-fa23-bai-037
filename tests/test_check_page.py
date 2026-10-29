"""Exercise assignment validation, including deliberate CI failure conditions."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_page', ROOT / 'scripts/check_page.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PageChecks(unittest.TestCase):
    def check_fixture(self, digit='1', section=None, transform=lambda x: x):
        section = section or '<h2>Skills</h2><ul>' + '<li>A skill</li>' * 4 + '</ul>'
        html = ('<html><head><title>Student portfolio</title><meta name="viewport" '
                'content="width=device-width"><link href="style.css" rel="stylesheet">'
                '</head><body><h1>Test Student</h1><p>ROLL' + digit + '</p>'
                '<section id="extra">' + section + '</section></body></html>')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(transform(html), encoding='utf-8')
            (root / 'style.css').write_text('body { color: black; }', encoding='utf-8')
            (root / 'student.json').write_text(json.dumps({'name': 'Test Student', 'roll_number': 'ROLL' + digit}), encoding='utf-8')
            return checker.check(root)

    def test_skills(self):
        self.assertEqual([], self.check_fixture())

    def test_missing_title_fails(self):
        self.assertTrue(any('title' in x for x in self.check_fixture(transform=lambda x: x.replace('<title>Student portfolio</title>', ''))))

    def test_wrong_roll_fails(self):
        self.assertTrue(any('roll_number' in x for x in self.check_fixture(transform=lambda x: x.replace('ROLL1', 'OTHER'))))

    def test_insufficient_skills_fails(self):
        self.assertTrue(self.check_fixture(section='<h2>Skills</h2><ul><li>Git</li></ul>'))

    def test_labs(self):
        section = '<h2>Labs</h2><ul>' + ''.join('<li>' + x + ': practice.</li>' for x in ('Git', 'GitHub', 'Docker', 'Actions')) + '</ul>'
        self.assertEqual([], self.check_fixture('5', section))
        self.assertTrue(self.check_fixture('5'))

    def test_contact(self):
        section = '<h2>Contact</h2><a href="mailto:student@example.org">Email</a><a href="https://github.com/student">GitHub</a>'
        self.assertEqual([], self.check_fixture('8', section))
        self.assertTrue(self.check_fixture('8'))

    def test_placeholder_fails(self):
        self.assertTrue(any('placeholders' in x for x in self.check_fixture(transform=lambda x: x.replace('</body>', '<p>YOUR_BIO</p></body>'))))


if __name__ == '__main__':
    unittest.main()
