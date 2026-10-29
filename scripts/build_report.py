"""Build the three-page submission: cover plus a two-page evidence report."""
import json
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'


def textbox(page, rect, text, size=10, bold=False, color=(0.12, 0.18, 0.23)):
    result = page.insert_textbox(fitz.Rect(rect), text, fontsize=size,
        fontname='hebo' if bold else 'helv', color=color, lineheight=1.3)
    if result < 0:
        raise RuntimeError('Report text does not fit: ' + text[:60])


def footer(page, number):
    textbox(page, (40, 812, 555, 832), f'Maha Ishaq | fa23-bai-037 | Assignment 2                                      {number}', 8)


def main():
    state = json.loads((EVIDENCE / 'remote-state.json').read_text())
    passed = state['successful_main_run_url']
    failed = state['deliberate_failed_run_url']
    observations = state['webhook_observations']
    ping = next(x for x in observations if x['event'] == 'ping')
    push = next(x for x in observations if x['event'] == 'push' and x['ref'] == 'refs/heads/feature-endpoint')
    pr = next(x for x in observations if x['event'] == 'pull_request' and x['action'] == 'opened')
    for name in ('container-browser', 'commit-history', 'merged-pr', 'dockerhub-tags', 'failed-actions', 'passed-actions'):
        if not (EVIDENCE / (name + '.png')).is_file():
            raise RuntimeError('Missing actual screenshot: ' + name)
    links = [
        ('Public GitHub repository', 'https://github.com/MahaIshaq04/devops-a2-fa23-bai-037'),
        ('Docker Hub repository', 'https://hub.docker.com/r/mahaishaq04/devops-a2'),
        ('Successful workflow run (main; published latest)', passed),
        ('Deliberately failed workflow run (missing title)', failed),
    ]
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    textbox(page, (44, 65, 551, 115), 'Assignment 2', 30, True)
    textbox(page, (44, 120, 551, 175), 'Build, Containerize and Automate\nDevOps for Cloud Computing - Lab Course', 15)
    textbox(page, (44, 205, 551, 265), 'Maha Ishaq\nRoll number: fa23-bai-037\nGitHub: MahaIshaq04 | Docker Hub: mahaishaq04', 12)
    y = 320
    for index, (label, url) in enumerate(links, 1):
        textbox(page, (44, y, 551, y + 27), f'{index}. {label}', 11, True)
        textbox(page, (44, y + 28, 551, y + 66), url, 9, color=(0.05, 0.27, 0.55))
        page.insert_link({'kind': fitz.LINK_URI, 'from': fitz.Rect(44, y + 26, 551, y + 65), 'uri': url})
        y += 90
    textbox(page, (44, 725, 551, 775), 'The following two pages contain the project report, actual webhook observations, and screenshots of the completed work.', 10)
    footer(page, 1)

    summary = ('This project is my personal HTML/CSS portfolio, with my name, roll number, and biography. '
               'My roll number ends in 7, so it includes a Contact section with my email and GitHub profile. '
               'nginx serves the page in Docker. GitHub Actions checks it, builds and tests the image, '
               'and publishes latest only after a push to main.')
    difference = ('The webhook sends event data as JSON to an external URL; it lets the receiver observe what happened. '
                  'GitHub Actions executes jobs inside a runner: it checks the page, builds and tests the container, '
                  'and publishes the image when the main-branch condition is satisfied.')
    problem = ('The first feature-PR smoke test failed with "curl: (56) Recv failure: Connection reset by peer". '
               'The request arrived while nginx was starting. I changed the readiness request to use '
               '--retry-all-errors with a 30-second retry limit. The next PR run passed, and the merged '
               'main run built, smoke-tested, and published latest successfully.')
    page = doc.new_page(width=595, height=842)
    textbox(page, (40, 28, 555, 68), 'Project report', 20, True)
    textbox(page, (40, 76, 555, 150), summary, 10)
    textbox(page, (40, 152, 555, 175), 'Observed webhook deliveries', 12, True)
    columns = [40, 150, 270, 424, 555]
    rows = [182, 210, 242, 280, 316]
    values = [
        ['Event', 'X-GitHub-Event', 'ref (push only)', 'Observation'],
        ['Ping', ping['event'], 'N/A', 'Hook creation sent a ping.'],
        ['Push', push['event'], push['ref'], 'Feature branch update was delivered.'],
        ['PR opened', pr['event'], 'N/A', 'action was opened.'],
    ]
    for row, values_row in enumerate(values):
        for col, value in enumerate(values_row):
            rect = fitz.Rect(columns[col], rows[row], columns[col + 1], rows[row + 1])
            page.draw_rect(rect, color=(0.7, 0.75, 0.78), fill=(0.92, 0.95, 0.96) if row == 0 else None, width=0.5)
            textbox(page, (rect.x0 + 5, rect.y0 + 4, rect.x1 - 5, rect.y1 - 2), value, 8, row == 0)
    textbox(page, (40, 325, 555, 385), difference, 9)
    textbox(page, (40, 391, 555, 412), 'A real problem and verified fix', 12, True)
    textbox(page, (40, 418, 555, 489), problem, 9)
    textbox(page, (40, 500, 555, 520), 'Container page in the browser (localhost:8080)', 10, True)
    page.insert_image(fitz.Rect(40, 525, 555, 798), filename=str(EVIDENCE / 'container-browser.png'), keep_proportion=True)
    footer(page, 2)

    page = doc.new_page(width=595, height=842)
    textbox(page, (40, 28, 555, 68), 'Screenshots of completed work', 20, True)
    screenshots = [
        ('commit-history', '1. Commit history: setup and feature work'),
        ('merged-pr', '2. feature-endpoint PR #1: merged'),
        ('dockerhub-tags', '3. Docker Hub: manual and latest tags'),
        ('failed-actions', '4. Deliberate missing-title run: failed'),
        ('passed-actions', '5. Main workflow: passed and published'),
    ]
    for i, (name, caption) in enumerate(screenshots):
        x = 40 + (i % 2) * 266
        y = 80 + (i // 2) * 235
        textbox(page, (x, y, x + 249, y + 32), caption, 9, True)
        page.insert_image(fitz.Rect(x, y + 34, x + 249, y + 225), filename=str(EVIDENCE / (name + '.png')), keep_proportion=True)
    textbox(page, (306, 585, 555, 725),
        'Evidence notes\n\nPR #2 deliberately removed the title, then restored it after the failure was recorded. '
        'It was closed without merging. The failed run remains available.\n\n'
        'Full-resolution screenshots are saved in the local evidence folder. '
        'The raw webhook receiver URL and payloads are kept out of the public repository.', 9)
    footer(page, 3)
    doc.save(ROOT / 'submission.pdf', garbage=4, deflate=True)
    doc.close()
    report = '# Assignment 2 report - Maha Ishaq (fa23-bai-037)\n\n'
    report += '\n'.join(f'- [{label}]({url})' for label, url in links)
    report += '\n\n## Project\n\n' + summary
    report += '\n\n## Webhook observations\n\n| Event | X-GitHub-Event | ref (push only) | Observation |\n| --- | --- | --- | --- |\n'
    report += '\n'.join('| ' + ' | '.join(row) + ' |' for row in values[1:])
    report += '\n\n' + difference + '\n\n## Problem and solution\n\n' + problem + '\n'
    (ROOT / 'docs/report.md').write_text(report, encoding='utf-8')
    print('Created submission.pdf: 3 pages (cover plus two-page report), with six actual screenshots.')


if __name__ == '__main__':
    main()
