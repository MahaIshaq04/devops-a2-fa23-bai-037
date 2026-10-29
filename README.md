# DevOps Assignment 2 — Portfolio

A plain HTML/CSS portfolio served by nginx in Docker. GitHub Actions checks the
page and running container on pushes to `main` and all pull requests. Only a push
to `main` publishes the verified image to Docker Hub as `latest`.

## Current status

This directory originally contained only `Assignment #2 (1).pdf`. The scaffold
is implemented, but is **not ready to submit** until personalized and the live
GitHub, Docker Hub, webhook, and report evidence steps below are completed.
No remote repository, commits, workflow runs, image uploads, or webhook deliveries
are claimed by this scaffold.

## Personalize first

1. Replace `YOUR_NAME`, `YOUR_ROLL_NUMBER`, and `YOUR_BIO` in `index.html`.
2. Fill in `student.json` with matching name and roll number and your two usernames.
3. Change the section with `id="extra"` according to the roll number's last digit:
   - **0–3:** Skills, with at least four list items (the default section).
   - **4–6:** Labs, with four list items describing Git, GitHub, Docker, and Actions.
   - **7–9:** Contact, with `mailto:your@email` and `https://github.com/your-user` links.
4. Keep the extra section for the `feature-endpoint` branch described below.
   In the initial page, temporarily omit that section. Add it on the branch.
5. Run `python scripts/check_page.py` after adding the section. CI deliberately
   fails while placeholders or required page content remain.

For an unpersonalized preview only: `python scripts/check_page.py --allow-placeholders`.
Open `index.html` directly to preview the design. The graded browser screenshot
must instead show the page served by the running Docker container.

## Git history and public repository (Part A)

Use your real Git identity. Create a **public**, empty GitHub repository named
`devops-a2-<roll-number>` in your account. Do not initialize it with a README.
Use the following sequence while building your actual history, substituting the
real username and roll number in the remote URL:

```powershell
git init -b main
git add .gitignore .dockerignore README.md
git commit -m "docs: describe portfolio setup and submission requirements"
git add index.html style.css student.json
git commit -m "feat: add personal HTML and CSS portfolio"
git add Dockerfile
git commit -m "build: serve portfolio with nginx"
git add scripts .github
git commit -m "ci: validate portfolio and publish verified Docker image"
git add docs
git commit -m "docs: add webhook evidence and report templates"
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/devops-a2-YOUR_ROLL_NUMBER.git
git push -u origin main
git switch -c feature-endpoint
# Now add your roll-number-specific extra section to index.html.
python scripts/check_page.py
git add index.html
git commit -m "feat: add roll-number-specific portfolio section"
git push -u origin feature-endpoint
```

Open a pull request from `feature-endpoint` to `main` in GitHub. Wait for the
checks, merge it yourself, and capture the merged PR and commit history. The base
page before the required extra section is added may fail the page check; the
feature PR should pass after that section is added. Do not manufacture a merged
PR with a local merge: the assignment requires an actual GitHub PR.

## Docker (Part B)

Start Docker Desktop with Linux containers and wait for the engine to be ready.
Replace `YOUR_DOCKERHUB_USERNAME` below. Create a Docker Hub repository named
`devops-a2`. Log in interactively using an access token, never commit a token.

```powershell
docker info
docker build -t YOUR_DOCKERHUB_USERNAME/devops-a2:manual .
docker run -d -p 8080:80 --name page YOUR_DOCKERHUB_USERNAME/devops-a2:manual
Invoke-WebRequest http://localhost:8080/ -UseBasicParsing
docker login --username YOUR_DOCKERHUB_USERNAME
docker push YOUR_DOCKERHUB_USERNAME/devops-a2:manual
```

Open **http://localhost:8080** in your browser and screenshot it with the address
bar visible. To stop and remove only this container: `docker rm -f page`.
The Docker build copies only the two public page files; reports and account
configuration are excluded from the image.

## GitHub Actions (Part C)

In repository Settings → Secrets and variables → Actions, create:

| Secret | Value |
| --- | --- |
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | A Docker Hub access token with permission to push images |

The workflow uses checkout v7 and Docker login v4, checked against their upstream
release pages: [checkout](https://github.com/actions/checkout/releases) and
[login-action](https://github.com/docker/login-action/releases).
It builds with the Docker CLI already present on the GitHub-hosted Ubuntu runner.
Pull requests need no Docker Hub credentials and cannot publish an image.

Keep one deliberately failed **GitHub Actions run** and one passed run:

```powershell
git switch main
git pull --ff-only
git switch -c demonstrate-failed-check
# Temporarily remove the <title> line from index.html.
git add index.html
git commit -m "test: demonstrate CI rejecting a missing page title"
git push -u origin demonstrate-failed-check
```

Open a PR to trigger the workflow (feature-branch pushes alone do not trigger it).
Capture the failing run and its exact error, restore the title, commit, and push
again. Capture the passed run and close this demonstration PR without merging.
Keep both run records. Also capture a successful `main` run that published
`latest`, and the Docker Hub tags page showing both `manual` and `latest`.

## Webhook and submission (Parts D and E)

Follow [the evidence checklist](docs/evidence-checklist.md). Configure the
webhook **before** making the push and opening the PR used for webhook evidence.
Fill in [the report template](docs/report-template.md), replacing all pending
fields with your own writing and real observations. Export it with the first-page
links as one PDF. Do not submit an unfilled template.

## Local verification

```powershell
python scripts/check_page.py
python -m unittest discover -s tests -v
```

The tests exercise failures and all three roll-number section rules using temporary
fixtures. They do not change your portfolio. Container checks require a working
Docker engine; remote runs and publication require your accounts.
