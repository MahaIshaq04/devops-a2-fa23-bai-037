# Completed assignment evidence

- [x] Portfolio personalized for Maha Ishaq, fa23-bai-037, with required Contact section.
- [x] Public repository: https://github.com/MahaIshaq04/devops-a2-fa23-bai-037
- [x] At least five meaningful setup commits plus feature and fix commits.
- [x] feature-endpoint pushed, PR #1 opened, CI passed, and PR merged.
- [x] nginx image built and container page served at http://localhost:8080.
- [x] Browser screenshot includes the actual address bar.
- [x] mahaishaq04/devops-a2:manual pushed to Docker Hub.
- [x] GitHub secrets DOCKERHUB_USERNAME and DOCKERHUB_TOKEN configured with an access token.
- [x] Passing main workflow published latest.
- [x] Deliberate missing-title branch/PR produced a retained failed run.
- [x] Title restored; repair run passed; demo PR #2 closed without merging.
- [x] Active application/json webhook configured for push and pull_request.
- [x] Actual ping, push, and pull_request opened deliveries captured.
- [x] Six actual screenshots and a three-page submission PDF generated locally.

## Actual observed webhook values

| Event | X-GitHub-Event | ref (push only) | Observation |
| --- | --- | --- | --- |
| Ping | ping | N/A | GitHub sent a ping after webhook creation. |
| Push | push | refs/heads/feature-endpoint | Pushing the feature branch produced a JSON delivery. |
| Pull request opened | pull_request | N/A | The JSON action field was opened. |

A webhook sends an event payload to an external receiver. GitHub Actions runs
configured jobs that check the page, build/test the container, and conditionally
publish the image. These deliveries were observed, not inferred from examples.

The private receiver URL, raw requests, and run metadata are saved in the ignored
`evidence/` directory. Do not add that directory to the public repository.
The PDF's first page contains direct repository and workflow-run links.

## Verified real problem

The feature-PR container smoke test failed with:

```text
curl: (56) Recv failure: Connection reset by peer
```

nginx had not finished starting. Changing curl's readiness retry to
`--retry-all-errors`, bounded by `--retry-max-time 30`, fixed it. The next feature
PR run passed and the merged main run successfully published latest.

## Submission

Open `submission.pdf`, review the report wording, and submit that single PDF.
Keep the GitHub repository public until marks are given. Full-resolution original
screenshots are kept locally in `evidence/` for inspection and regeneration.
