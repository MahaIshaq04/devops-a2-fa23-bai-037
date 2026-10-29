"""Check the actual assignment requirements using only the Python standard library."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.text = []
        self.links = []
        self.in_extra = False
        self.extra_text = []
        self.extra_items = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == 'section' and attrs.get('id') == 'extra':
            self.in_extra = True
        if self.in_extra and tag == 'li':
            self.extra_items += 1
        if tag in ('a', 'link'):
            self.links.append(attrs.get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'section':
            self.in_extra = False

    def handle_data(self, data):
        self.text.append(data)
        if self.in_extra:
            self.extra_text.append(data)


def check(root, allow_placeholders=False):
    errors = []
    for filename in ('index.html', 'style.css', 'student.json'):
        if not (root / filename).is_file():
            errors.append(f'Missing {filename}')
    if errors:
        return errors
    source = (root / 'index.html').read_text(encoding='utf-8')
    css = (root / 'style.css').read_text(encoding='utf-8')
    student = json.loads((root / 'student.json').read_text(encoding='utf-8'))
    page = Page()
    page.feed(source)
    visible = ' '.join(page.text)
    extra = ' '.join(page.extra_text)
    if not re.search(r'<title>\s*[^<\s][^<]*</title>', source, re.I):
        errors.append('A nonempty <title> is required')
    if 'style.css' not in page.links or not css.strip():
        errors.append('Link a nonempty style.css')
    if any(tag == 'script' for tag, _ in page.tags):
        errors.append('Use plain HTML and CSS only')
    for key in ('name', 'roll_number'):
        if not student.get(key) or student[key] not in visible:
            errors.append(f'The configured {key} must appear on the page')
    if not any(tag == 'meta' and attrs.get('name') == 'viewport' for tag, attrs in page.tags):
        errors.append('Add a viewport meta tag for mobile screens')
    placeholders = re.findall(r'YOUR_[A-Z_]+', source + json.dumps(student))
    if placeholders and not allow_placeholders:
        errors.append('Replace personalization placeholders: ' + ', '.join(sorted(set(placeholders))))
    roll = student.get('roll_number', '')
    if roll and roll[-1].isdigit():
        digit = int(roll[-1])
        if digit <= 3 and ('Skills' not in extra or page.extra_items < 4):
            errors.append('Roll ending 0-3 needs a Skills section with at least four skills')
        elif 4 <= digit <= 6:
            if 'Labs' not in extra or page.extra_items < 4 or not all(x in extra for x in ('Git', 'GitHub', 'Docker', 'Actions')):
                errors.append('Roll ending 4-6 needs Labs with Git, GitHub, Docker, and Actions descriptions')
        elif digit >= 7:
            if 'Contact' not in extra or not any(x.startswith('mailto:') and '@' in x for x in page.links) or not any(x.startswith('https://github.com/') for x in page.links):
                errors.append('Roll ending 7-9 needs Contact with email and GitHub profile links')
    elif not allow_placeholders:
        errors.append('Roll number must end in a digit')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--allow-placeholders', action='store_true', help='Scaffold preview only; never used in CI')
    args = parser.parse_args()
    try:
        problems = check(args.root, args.allow_placeholders)
    except (ValueError, OSError) as exc:
        problems = [str(exc)]
    for problem in problems:
        print(f'FAIL: {problem}')
    if problems:
        raise SystemExit(1)
    print('PASS: portfolio requirements' + (' (scaffold preview; personalization not verified)' if args.allow_placeholders else ''))
