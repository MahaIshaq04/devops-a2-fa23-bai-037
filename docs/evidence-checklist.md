# Submission evidence checklist

## Live work still required

- [ ] Fill personal details and choose the correct extra section.
- [ ] Create public GitHub repository `devops-a2-<roll-number>`.
- [ ] Make at least five meaningful commits using your own Git identity.
- [ ] Push `feature-endpoint`, open its PR, and merge it yourself.
- [ ] Build and run the image locally; screenshot browser at http://localhost:8080.
- [ ] Push `<dockerhub-username>/devops-a2:manual`.
- [ ] Configure the two GitHub Actions secrets using a Docker Hub access token.
- [ ] Keep a deliberate failed PR run and a later passed run.
- [ ] Verify successful main run publishes `latest`.
- [ ] Screenshot Docker Hub showing `manual` and `latest`.
- [ ] Record actual webhook deliveries below.
- [ ] Write report in your own words, add screenshots, export one submission PDF.

## Webhook setup and observations

1. Open https://webhook.site and copy your unique receiver URL. Treat that URL
   and captured payloads as private; do not commit them to the public repository.
2. In GitHub repository Settings → Webhooks → Add webhook, set that URL,
   content type `application/json`, and select **Pushes** and **Pull requests**.
   Keep the webhook active. GitHub sends a ping when the hook is created.
3. Push a commit, then open a new PR. Inspect each request at webhook.site and
   in GitHub's Recent Deliveries. Record header names and exact observed values.
4. Use the actual `X-GitHub-Event` header, top-level `ref` for a push, and
   `action` for a PR. A PR-opened delivery uses event `pull_request` plus action
   `opened`; the event header does not include the word `opened`.
5. Fill the report table from these deliveries. Ping and PR top-level push `ref`
   are not applicable; do not substitute the PR's nested branch name.

The report needs six screenshots: history, merged PR, Docker Hub tags, failed
Actions run, passed Actions run, and container-served page with address bar.
Keep original images in the ignored `evidence/` directory. Avoid capturing tokens.

## Problems observed during scaffolding

Docker's initial local probe reported:

```text
failed to connect to the docker API at npipe:////./pipe/docker_engine
The system cannot find the file specified.
```

The engine was unavailable. Starting Docker Desktop is the next diagnostic step;
a successful build/run has **not** yet verified the fix. Only describe this as
solved in your report after you actually verify it. GitHub CLI was also absent,
and this directory was initially not a Git repository.
