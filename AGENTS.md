# Project credential handling

- Use collaborator-provided API credentials only for the interphAIse workflow and its minimal authentication/smoke tests. Do not use them for other projects or unrelated tasks.
- Before starting paid workflow runs with a newly configured credential, perform one minimal authentication/smoke test against the intended provider/model. Report success/failure without printing the credential or raw request headers.
- Read credentials from the local, git-ignored `.env` or environment. Never hardcode, print, copy into reports, embed in command arguments, or commit credentials. Do not expose raw environment dumps or provider debug logs.
- Keep `.env` untracked and ignored. Never force-add it. Before committing or pushing credential-related changes, verify that no secrets or local credential files are included.
- `.env.example` is a public template and must contain placeholders only. Preserve it for collaborators.
- If a credential is missing, ask the user to enter it locally; do not ask them to paste it into chat.

- The collaborator Anthropic credential is authorised only for Claude Haiku 5.5 (`claude-haiku-5-5`). Use the direct Anthropic endpoint; never route it to OpenRouter or fall back to another model.

- All live project LLM calls are locked to the configured Haiku 5.5 model and the Anthropic credential. Do not use other providers or credentials even if they are available.

# Development reporting

- After every substantive work session, update `DEVELOPMENT_LOG.md` before handing the work back. This is an explicit user requirement: a human or another LLM must be able to follow the process and continue it.
- Record the date, branch, purpose, changes and relevant files, reasons for important decisions, verification actually performed and its results, unresolved limitations, and concrete next steps. Include the implementation commit when known; never invent a commit or test result.
- Distinguish implemented, tested, proposed and unfinished work. State whether live API/LLM/MLIP runs occurred, without exposing credentials. Record reproducibility commands, dataset/objective versions and hashes when relevant.
- Preserve earlier log entries; append a new dated checkpoint. Correct earlier mistakes explicitly instead of silently rewriting the history.
- Keep `REPORT.md` aligned when project status or scientific conclusions change. Link detailed handoff documents rather than duplicating them. Documentation-only edits need a consistency/diff check, not an unnecessary full test run.
- At the start of substantive work, read the latest log entry and the relevant handoff documents alongside these instructions.

# Niflheim compute access

- The user authorizes heavier interphAIse calculations on Niflheim via `ssh fjorm`, working under `/home/scratch12/davti/OSI_Hackathon`.
- Use Slurm allocations for heavy calculations; use the login host for inspection, transfers and job submission. Keep this project's files/jobs separate from unrelated work.
- Consult `NIFLHEIM.md` for verified access and setup status. Do not assume a PET-MAD environment or GPU allocation is already configured.
- Transfer explicit project inputs and code. Keep `.env` and API credentials local; offline MLIP jobs do not need them. Record the source commit, checkpoint hash, Slurm job ID, resource request, convergence and compute usage in the report.
