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

**Live, verified on 22 October 2026:**
[Open the referee explorer](https://davidetisi.github.io/interphAIse/) or
[download the offline ZIP](https://davidetisi.github.io/interphAIse/interphaise-referee-viewer.zip).
Both were fetched without authentication and matched the local SHA-256 values.
The public page rendered the actual paired structures with no JavaScript errors.
The source repository remains **private**; this website does not make its code
or Git history public. The user will change repository visibility after the
final merge, separately, to meet the hackathon submission requirement.

The standalone deployment is `gh-pages` commit `6853ef6`, built from integration
source `a727582`. It contains only the five allowlisted files below. The API
reported Pages as already enabled when creation was attempted; a subsequent
read confirmed `status: built`, `public: true`, and `gh-pages` at `/` as source.
No paid plan or repository visibility setting was changed.

The checked release ZIP is also stored in
`presentations/results_2026-10-22/interphaise_referee_viewer_2026-10-22.zip`.
HTML SHA-256: `893ae8839664d6834e79b6d32e1b3c3aaa6a10e9011e348f0efc3ba698b7a14d`.
ZIP SHA-256: `88868e10ec3359050bd2eac4c5d2e2c6a956f4001377818657518939727d7e0d`.

[GitHub's documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
states that Pages from private repositories requires Pro, Team or Enterprise.
Do not make the source repository public merely to host the viewer.

For later updates, preserve the dedicated `gh-pages` branch and publish **only**
these generated files at its root from a separate checkout:

- `index.html`
- `evidence.json`
- `README.txt`
- `.nojekyll`
- `interphaise-referee-viewer.zip`

The branch now exists; update its existing history instead of replacing it.
Do not copy a repository directory or use a broad
upload command. Keep `.env`, prompts, archives and unrelated project files out.
Pages already deploys that branch's root. Read its configuration with:

```bash
gh api repos/DavideTisi/interphAIse/pages
```

After an update, verify the page and ZIP again **without authentication** and
compare their hashes with the local release. Do not use a paid upgrade or change
repository visibility as part of a routine viewer deployment. The complete ZIP
also works as a submission attachment and does not depend on hosting.

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

No materials/LLM API call, new calculation, GPU job or paid service was used.
GitHub API calls were used only to inspect/configure the static hosting.
