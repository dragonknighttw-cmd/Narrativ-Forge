# OpenCode Free Model Setup

> Last checked: 2026-10-09  
> Scope: OpenCode project configuration using OpenRouter free endpoints.  
> Evidence status: repository configuration only; real account access and model execution must still be tested locally.

## Default model

The project-level `opencode.json` defaults to:

- **Cohere North Mini Code (Free)** — `openrouter/cohere/north-mini-code:free`

OpenRouter currently lists this as a free agentic coding model and specifically notes training across coding-agent harnesses including OpenCode. It supports tool calling. Free endpoints can still be rate-limited or unavailable.

## Configured alternatives

Use OpenCode's `/models` command to select one of these configured models if the default is unavailable or performs poorly:

| Display name | OpenRouter model ID | Notes |
|---|---|---|
| NVIDIA Nemotron 3.5 Lightning (Free) | `openrouter/nvidia/nemotron-3.5-lightning:free` | General agentic workload; free endpoint currently supports tool calling. |
| NVIDIA Nemotron 3 Ultra (Free) | `openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` | Longer reasoning and agentic tasks; availability is subject to free endpoint limits. |
| Thinking Machines Inkling Small (Free) | `openrouter/thinkingmachines/inkling-small:free` | Coding and tool-use model; the provider states free-endpoint prompts and outputs are logged and used to improve its models. Do not use with confidential information or personal data. |

Free model catalogs, names, terms, quotas, and endpoint availability change. Re-check the [OpenRouter Free Models collection](https://openrouter.ai/collections/free-models) before relying on a model for ongoing work.

## First-time setup on Windows

1. Install OpenCode and open a terminal in the repository root.
2. Run `opencode`.
3. Run `/connect`, choose **OpenRouter**, and enter the API key. OpenCode stores credentials in its user-level auth store; do not put API keys in this repository.
4. Restart OpenCode or reload the project configuration if needed.
5. The default model is configured in `opencode.json`. Run `/models` to choose a configured alternative.
6. Send the smoke-test prompt below and inspect the generated diff before accepting changes.

## Smoke test

Ask OpenCode:

```text
Inspect this repository without modifying files.
Explain the top-level project structure and identify the test commands for the frontend and backend.
Do not read, print, or reveal any .env files, credentials, tokens, or private user data.
Cite the repository files that support your summary.
```

Then, only after the model answers correctly, test a small isolated code change on a disposable branch or test file. Review `git diff`, run the narrowest relevant tests, and do not let the model push changes automatically.

## Security and privacy

- A `:free` suffix means the listed endpoint is currently priced at zero, not that it has guaranteed uptime, unlimited usage, or private processing.
- Do not send API keys, secrets, cookies, real `.env` contents, private user data, confidential media, or production database records to a free model.
- Some providers explicitly retain prompts/outputs or use them to improve models. Check the individual model page and provider terms before sending repository contents.
- OpenCode's repository permissions remain intentionally cautious: shell commands require approval by default, file reads are allowed, edits are allowed, and `git push` is denied.
- Model configuration is not proof of live provider health. Mark a model VERIFIED only after a real request succeeds and the smoke test is reviewed.

## Official references

- [OpenCode models configuration](https://docs.opencode.ai/docs/models/)
- [OpenCode OpenRouter provider setup](https://docs.opencode.ai/docs/providers/)
- [OpenRouter Free Models](https://openrouter.ai/collections/free-models)
- [Cohere North Mini Code (Free)](https://openrouter.ai/cohere/north-mini-code:free)
- [NVIDIA Nemotron 3.5 Lightning (Free)](https://openrouter.ai/nvidia/nemotron-3.5-lightning:free)
- [NVIDIA Nemotron 3 Ultra (Free)](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free)
- [Thinking Machines Inkling Small (Free)](https://openrouter.ai/thinkingmachines/inkling-small:free)
