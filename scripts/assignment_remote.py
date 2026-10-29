"""Run the assignment's live GitHub steps using Git Credential Manager.

No credentials are written to disk or printed. Local evidence stays gitignored.
Optional dependencies are installed into .tools for secret encryption.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools'))
EVIDENCE = ROOT / 'evidence'
STATE = EVIDENCE / 'remote-state.json'
REPO = 'MahaIshaq04/devops-a2-fa23-bai-037'
BASE = 'https://api.github.com/repos/' + REPO


def request(url, method='GET', data=None, token=None):
    headers = {'User-Agent': 'devops-assignment-2', 'Accept': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    if data is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, headers=headers, method=method,
                                 data=json.dumps(data).encode() if data is not None else None)
    with urllib.request.urlopen(req, timeout=45) as response:
        body = response.read()
        return json.loads(body) if body else {}


def credential():
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
    result = subprocess.run(['git', 'credential', 'fill'],
                            input='protocol=https\nhost=github.com\n\n',
                            capture_output=True, text=True, env=env, check=True)
    fields = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    return fields['password']


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save(state):
    EVIDENCE.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding='utf-8')


def main(command):
    token = credential()
    state = load()
    api = lambda path, method='GET', data=None: request(BASE + path, method, data, token)
    if command == 'secrets':
        from nacl.public import PublicKey, SealedBox
        config = json.loads((Path.home() / '.docker/config.json').read_text())
        helper = config.get('credsStore') or config['credHelpers']['https://index.docker.io/v1/']
        result = subprocess.run(['docker-credential-' + helper, 'get'],
                                input='https://index.docker.io/v1/\n',
                                capture_output=True, text=True, check=True)
        docker = json.loads(result.stdout)
        if docker['Username'] != 'mahaishaq04':
            raise RuntimeError('Docker login belongs to another username')
        if not docker['Secret'].startswith(('dckr_pat_', 'dckr_oat_')):
            raise RuntimeError('Refusing to use a password instead of an access token')
        key = api('/actions/secrets/public-key')
        box = SealedBox(PublicKey(base64.b64decode(key['key'])))
        for name, value in {'DOCKERHUB_USERNAME': docker['Username'], 'DOCKERHUB_TOKEN': docker['Secret']}.items():
            encrypted = base64.b64encode(box.encrypt(value.encode())).decode()
            api('/actions/secrets/' + name, 'PUT', {'encrypted_value': encrypted, 'key_id': key['key_id']})
            print('Configured secret:', name)
    elif command == 'hook':
        if not state.get('webhook_uuid'):
            receiver = request('https://webhook.site/token', 'POST', {'default_status': 200})
            state['webhook_uuid'] = receiver['uuid']
            save(state)
        if not state.get('hook_id'):
            hook = api('/hooks', 'POST', {'name': 'web', 'active': True,
                'events': ['push', 'pull_request'],
                'config': {'url': 'https://webhook.site/' + state['webhook_uuid'], 'content_type': 'json', 'insecure_ssl': '0'}})
            state['hook_id'] = hook['id']
            save(state)
        print('Configured active webhook for push and pull_request; private receiver saved in evidence.')
    elif command == 'pr':
        prs = api('/pulls?state=all&head=MahaIshaq04:feature-endpoint')
        pr = prs[0] if prs else api('/pulls', 'POST', {
            'title': 'Add required Contact section for fa23-bai-037',
            'head': 'feature-endpoint', 'base': 'main',
            'body': 'Adds Maha Ishaq\'s email and GitHub profile because the roll number ends in 7. Finalizes the supplied biography and Docker Hub username.\n\nValidation: portfolio checker and seven validator tests pass locally. Docker image builds and serves the page at localhost:8080.'})
        state['feature_pr'] = pr['number']
        state['feature_pr_url'] = pr['html_url']
        save(state)
        print('Feature PR:', pr['html_url'])
    elif command == 'status':
        runs = api('/actions/runs?per_page=30')['workflow_runs']
        state['runs'] = [{k: r.get(k) for k in ('id', 'html_url', 'head_branch', 'head_sha', 'event', 'status', 'conclusion', 'run_number')} for r in runs]
        successful = [r for r in runs if r['head_branch'] == 'main' and r['event'] == 'push' and r['conclusion'] == 'success']
        if successful:
            state['successful_main_run_url'] = successful[0]['html_url']
            state['successful_main_run_id'] = successful[0]['id']
        save(state)
        for r in state['runs']:
            print(r['id'], r['head_branch'], r['event'], r['status'], r['conclusion'], r['html_url'])
            if r['conclusion'] == 'failure':
                for job in api('/actions/runs/' + str(r['id']) + '/jobs')['jobs']:
                    print('  Job:', job['name'], [(s['name'], s['conclusion']) for s in job['steps'] if s['conclusion'] == 'failure'])
                    for a in api('/check-runs/' + str(job['check_run_url'].split('/')[-1]) + '/annotations'):
                        print('  Annotation:', a.get('message', '')[:1500])
    elif command == 'merge':
        number = state['feature_pr']
        pr = api('/pulls/' + str(number))
        checks = api('/commits/' + pr['head']['sha'] + '/check-runs')['check_runs']
        if not checks or any(c['conclusion'] != 'success' for c in checks):
            raise RuntimeError('Feature PR checks have not all succeeded; refusing to merge')
        result = api('/pulls/' + str(number) + '/merge', 'PUT', {
            'merge_method': 'merge', 'sha': pr['head']['sha'],
            'commit_title': 'Merge Contact section for fa23-bai-037'})
        if not result.get('merged'):
            raise RuntimeError('GitHub did not merge the PR')
        state['merge_sha'] = result['sha']
        save(state)
        print('Merged feature PR:', state['feature_pr_url'])
    elif command == 'deliveries':
        data = request('https://webhook.site/token/' + state['webhook_uuid'] + '/requests?sorting=newest')
        (EVIDENCE / 'webhook-requests.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
        summary = []
        for r in data.get('data', []):
            headers = {k.lower(): v for k, v in r.get('headers', {}).items()}
            event = headers.get('x-github-event')
            if isinstance(event, list):
                event = event[0]
            try:
                payload = json.loads(r.get('content', '{}'))
            except (ValueError, TypeError):
                continue
            if event:
                item = {'event': event, 'ref': payload.get('ref') if event == 'push' else None,
                        'action': payload.get('action'), 'request_uuid': r['uuid']}
                summary.append(item)
                print(json.dumps(item))
        state['webhook_observations'] = summary
        save(state)
    elif command == 'demo-open':
        branch = 'demonstrate-failed-check'
        if not state.get('demo_branch'):
            head = api('/git/ref/heads/main')['object']['sha']
            api('/git/refs', 'POST', {'ref': 'refs/heads/' + branch, 'sha': head})
            state['demo_branch'] = branch
            save(state)
            content = api('/contents/index.html?ref=' + branch)
            source = base64.b64decode(content['content']).decode()
            import re
            source = re.sub(r'\s*<title>.*?</title>', '', source)
            api('/contents/index.html', 'PUT', {'message': 'test: demonstrate CI rejecting missing title',
                'branch': branch, 'sha': content['sha'],
                'content': base64.b64encode(source.encode()).decode()})
        if not state.get('demo_pr'):
            pr = api('/pulls', 'POST', {'title': 'Demonstrate missing-title CI failure (do not merge)',
                'head': branch, 'base': 'main',
                'body': 'Intentionally removes the page title to prove the custom check rejects an invalid page. The title will be restored after the failed run is recorded; this PR will be closed without merging.'})
            state['demo_pr'] = pr['number']
            state['demo_pr_url'] = pr['html_url']
            save(state)
        print('Demonstration PR:', state['demo_pr_url'])
    elif command == 'demo-fix':
        runs = api('/actions/runs?branch=demonstrate-failed-check&per_page=20')['workflow_runs']
        failed = [r for r in runs if r['conclusion'] == 'failure']
        if not failed:
            raise RuntimeError('Wait for the deliberate failed run before restoring the title')
        state['deliberate_failed_run_url'] = failed[0]['html_url']
        state['deliberate_failed_run_id'] = failed[0]['id']
        original = api('/contents/index.html?ref=main')
        current = api('/contents/index.html?ref=demonstrate-failed-check')
        if original['sha'] != current['sha']:
            api('/contents/index.html', 'PUT', {'message': 'fix: restore page title after failed CI demonstration',
                'branch': 'demonstrate-failed-check', 'sha': current['sha'], 'content': original['content']})
        save(state)
        print('Retained failed run:', state['deliberate_failed_run_url'])
    elif command == 'demo-close':
        pr = api('/pulls/' + str(state['demo_pr']))
        checks = api('/commits/' + pr['head']['sha'] + '/check-runs')['check_runs']
        if not checks or any(c['conclusion'] != 'success' for c in checks):
            raise RuntimeError('Wait for the restored-title run to pass before closing the demo PR')
        api('/pulls/' + str(state['demo_pr']), 'PATCH', {'state': 'closed'})
        print('Closed demonstration PR without merging.')
    else:
        raise ValueError('Unknown operation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['secrets', 'hook', 'pr', 'status', 'merge', 'deliveries', 'demo-open', 'demo-fix', 'demo-close'])
    try:
        main(parser.parse_args().command)
    except urllib.error.HTTPError as exc:
        # Only print GitHub's human-readable message, never request headers.
        try:
            detail = json.loads(exc.read()).get('message', '')
        except ValueError:
            detail = exc.reason
        print(f'HTTP {exc.code}: {detail}', file=sys.stderr)
        raise SystemExit(1)
