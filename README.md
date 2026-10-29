# Maha Ishaq - DevOps Assignment 2

A plain HTML/CSS portfolio for **Maha Ishaq**, roll **fa23-bai-037**.
Because the roll number ends in 7, the page includes a Contact section with
email and GitHub profile links. nginx serves the two page files from Docker.

## Project links

- [Public GitHub repository](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037)
- [Docker Hub tags](https://hub.docker.com/r/mahaishaq04/devops-a2/tags)
- [Merged feature-endpoint PR](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037/pull/1)
- [Actions runs](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037/actions)
- [Missing-title demonstration PR](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037/pull/2)

## Run and check

Start Docker Desktop with Linux containers, then:

```powershell
python scripts/check_page.py
python -m unittest discover -s tests -v
docker build -t mahaishaq04/devops-a2:manual .
docker run -d -p 8080:80 --name page mahaishaq04/devops-a2:manual
```

Open **http://localhost:8080**. If the `page` container already exists, use
`docker start page` instead of creating another container. After editing the
page, rebuild the image and replace that container to serve the updated files.
Publish manually with `docker push mahaishaq04/devops-a2:manual`.
Use `docker login --username mahaishaq04` with an access token when login is
needed. Never commit credentials. Stop/remove this container with `docker rm -f page`.

## Git and CI

Five meaningful setup commits precede the `feature-endpoint` branch. The Contact
section was added on that branch, pushed, checked by CI, and merged through
GitHub PR #1. Keep the repository public until grading is finished.

`.github/workflows/ci.yml` runs on pushes to `main` and every pull request:

1. Check the title, stylesheet, actual name and roll number, mobile viewport,
   absence of JavaScript, and roll-number-specific extra section.
2. Run seven tests covering valid sections and rejected invalid pages.
3. Build the Docker image and compare served HTML/CSS with the source files.
4. On a push to `main` only, log in using `DOCKERHUB_USERNAME` and
   `DOCKERHUB_TOKEN` GitHub secrets, then push the verified image as `latest`.

PR builds never log in or publish. The startup check retries transient nginx
connection resets within a time limit. Its initial failure and successful fix
are preserved in Actions. PR #2 separately demonstrates that deleting `<title>`
fails the custom check; the title is restored without merging the demo.

## Webhook and report

The active repository webhook sends JSON for push and pull-request events to a
unique webhook.site receiver. Actual ping, push, and PR-opened deliveries are
saved privately under `evidence/`. The receiver URL and raw payloads are ignored
by Git. See [the evidence checklist](docs/evidence-checklist.md).

`submission.pdf` is generated locally with the required first-page links and
the report/evidence after it. Review the report wording before submitting.
The PDF and full-resolution screenshots stay outside the public source history.

## Optional evidence helpers

`scripts/assignment_remote.py` uses the existing Git Credential Manager login.
Secret setup accepts only a Docker access token, encrypts it with GitHub's public
key, and never prints or stores it. It needs PyNaCl under `.tools/`; screenshot
capture additionally needs Playwright, Pillow, and Edge. These Windows helpers
are not needed by CI.

`scripts/capture_evidence.py` captures actual public pages and a real browser
window showing the container URL. `scripts/build_report.py` creates the PDF
from those files and verified run URLs. Neither fabricates external evidence.
