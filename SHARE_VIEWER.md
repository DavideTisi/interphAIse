# Sharing the structure explorer with referees

Build the compact referee edition from archived evidence:

```bash
python scripts/build_referee_viewer.py --output runs/referee-site
```

Send `runs/referee-site/interphaise-referee-viewer.zip`. The recipient extracts it
and opens `index.html` in an ordinary browser with JavaScript enabled. No Python,
login, API key or internet connection is required. The approximately 1.4 MB HTML
contains the six selected primary contacts; the ZIP is approximately 268 KB.
For the complete research catalogue, use `python scripts/build_structure_viewer.py`.

The compact edition shows three coating buttons, paired cathode/electrolyte
structures, element/component/constraint colouring, rotation, cell controls and
XYZ/PNG downloads. The exported geometry and primary values are unchanged.
`evidence.json` records the index/geometry hashes, values and limitations.
The guard refuses incomplete evidence, local home paths, remote assets and
output folders containing unrelated files.

This is supporting visual evidence for the hackathon presentation. It explains
what the atomistic calculations model; it is not evidence by itself that the
LLM reasons well or that a coating improves battery performance. The page keeps
LiF uncomputed, the polar-model limitation, the small Nb–Ta difference and the
unquantified CaAl sensitivities visible. Later sensitivity information is
distinguished from the primary evidence available during the live pilot.

## Hosting status and publication

At inspection on 2026-10-22, `DavideTisi/interphAIse` is **private**, the authenticated
user has repository admin rights, and `GET /repos/DavideTisi/interphAIse/pages`
returns 404: no Pages site is configured. The account API did not expose a plan.
There is **no verified public viewer URL yet**.

[GitHub's documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
states that Pages from private repositories requires Pro, Team or Enterprise.
Do not make the source repository public merely to host the viewer.

To publish after review, create a dedicated `gh-pages` branch with **only** these
generated files at its root, using a separate empty checkout:

- `index.html`
- `evidence.json`
- `README.txt`
- `.nojekyll`
- `interphaise-referee-viewer.zip`

Check that the remote branch does not already exist before creating it; preserve
any existing deployment. Do not copy a repository directory or use a broad
upload command. Keep `.env`, prompts, archives and unrelated project files out.
Configure GitHub Pages to deploy that branch's root, keeping repository
visibility private. The API request is:

```bash
gh api --method POST repos/DavideTisi/interphAIse/pages \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'
```

This request may be refused if the account plan does not support private-repo
Pages. It must not trigger a paid upgrade or a repository-visibility change.
If it succeeds, read the returned `html_url`, wait for the build, and verify that
the page and ZIP load **without authentication** and that the delivered HTML
matches the local hash. Until then, do not label the anticipated URL as live.
If unavailable, the complete ZIP is already suitable as a hackathon attachment;
a separate public results-only repository or another static host is an optional
publishing decision, not a reason to expose the research repository.

## Verification performed

The focused viewer/export suite passed 25 tests. Browser checks displayed Nb,
Ta and CaAl primary contacts, matching metrics, component colouring and the
oblique view, with no JavaScript warnings/errors. The test suite verifies the
ZIP's HTML is byte-identical to the hosted HTML, preserves exact structures and
contains only the four offline files. A browser download-event wait did not
complete and was interrupted; no successful browser-download test is claimed.
The page and download can be checked locally with:

```bash
python -m http.server 8879 --bind 127.0.0.1 --directory runs/referee-site
python -m pytest tests/test_referee_viewer.py tests/test_structure_viewer.py -q
```

No new API call, materials calculation, GPU job or paid service was used.
