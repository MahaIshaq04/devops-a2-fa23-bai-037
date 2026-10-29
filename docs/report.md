# Assignment 2 report - Maha Ishaq (fa23-bai-037)

- [Public GitHub repository](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037)
- [Docker Hub repository](https://hub.docker.com/r/mahaishaq04/devops-a2)
- [Successful workflow run (main; published latest)](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037/actions/runs/40900600598)
- [Deliberately failed workflow run (missing title)](https://github.com/MahaIshaq04/devops-a2-fa23-bai-037/actions/runs/40900751200)

## Project

This project is my personal HTML/CSS portfolio, with my name, roll number, and biography. My roll number ends in 7, so it includes a Contact section with my email and GitHub profile. nginx serves the page in Docker. GitHub Actions checks it, builds and tests the image, and publishes latest only after a push to main.

## Webhook observations

| Event | X-GitHub-Event | ref (push only) | Observation |
| --- | --- | --- | --- |
| Ping | ping | N/A | Hook creation sent a ping. |
| Push | push | refs/heads/feature-endpoint | Feature branch update was delivered. |
| PR opened | pull_request | N/A | action was opened. |

The webhook sends event data as JSON to an external URL; it lets the receiver observe what happened. GitHub Actions executes jobs inside a runner: it checks the page, builds and tests the container, and publishes the image when the main-branch condition is satisfied.

## Problem and solution

The first feature-PR smoke test failed with "curl: (56) Recv failure: Connection reset by peer". The request arrived while nginx was starting. I changed the readiness request to use --retry-all-errors with a 30-second retry limit. The next PR run passed, and the merged main run built, smoke-tested, and published latest successfully.
