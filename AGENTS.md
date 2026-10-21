# Project credential handling

- Use collaborator-provided API credentials only for the interphAIse workflow and its minimal authentication/smoke tests. Do not use them for other projects or unrelated tasks.
- Before starting paid workflow runs with a newly configured credential, perform one minimal authentication/smoke test against the intended provider/model. Report success/failure without printing the credential or raw request headers.
- Read credentials from the local, git-ignored `.env` or environment. Never hardcode, print, copy into reports, embed in command arguments, or commit credentials. Do not expose raw environment dumps or provider debug logs.
- Keep `.env` untracked and ignored. Never force-add it. Before committing or pushing credential-related changes, verify that no secrets or local credential files are included.
- `.env.example` is a public template and must contain placeholders only. Preserve it for collaborators.
- If a credential is missing, ask the user to enter it locally; do not ask them to paste it into chat.

- The collaborator Anthropic credential is authorised only for Claude Haiku 5.5 (`claude-haiku-5-5`). Use the direct Anthropic endpoint; never route it to OpenRouter or fall back to another model.
