# LLZO chemistry caveat and selection audit

21 October 2026. Post-hoc review of the unchanged frozen LLZO table and
production archive at `work/agent-experiments:06a4271`. No new experiment,
filtered-pool rerun, significance test or change to the primary endpoint.

**Yes: state the practical-coating caveat and count the flagged compounds.
Keep random's 24/30 versus iterative's 12/30 as the primary result.** The
selection traces support late, concentrated adaptation; they do not establish
that Haiku deliberately rejected particular compounds for safety.

## What is in the acceptable set

There are 17 acceptable structure IDs, representing ten formulas. Five IDs
(29.4%) belong to three oxyhalogen formulas worth separate practical review:

| Formula | Structure IDs | Evidence level |
|---|---|---|
| LiIO3, lithium iodate | mp-aaaabhyx, mp-aaaabiak, mp-aaaabipk | Supplier classifies it as an oxidising solid |
| LiClO4, lithium perchlorate | mp-aaaabsvl | Supplier classifies it as an oxidising solid |
| Li5IO6, lithium orthoperiodate | mp-aaacqxqk | I(VII) periodate identity; chemical-family flag, compound-specific GHS classification not verified |

The directly supplier-classified subset is therefore four IDs. The broader
review set is five. Li5IO6 is an **orthoperiodate**, not an iodate. Sources:
[ESPI LiIO3 SDS](https://www.espimetals.com/msds/648-Lithium%20Iodate),
[Sigma LiClO4](https://www.sigmaaldrich.com/US/en/product/aldrich/931969), and
[primary Li5IO6 identification paper](https://www.jstage.jst.go.jp/article/bunsekikagaku1952/26/3/26_3_191/_pdf).

Use “flagged for practical review,” not “proven unusable coatings.” An oxidiser
classification alone does not settle suitability in every battery context;
the cited LiClO4 supplier also describes electrolyte applications. Neither
that application nor benchmark acceptance validates its use as this coating.
The remaining twelve IDs are merely unflagged by this narrow annotation,
not established safe or functional coatings. This is not a complete hazard
screen of all 141 candidates.

## How much of random's advantage involves these compounds?

All original ten-query trajectories are retained:

| Arm | Distinct formulas | Acceptable picks / 300 | Flagged acceptable picks | Successful runs / 30 | Runs with an unflagged acceptable hit |
|---|---:|---:|---:|---:|---:|
| Random | 95 | 33 | 11 | 24 | 18 |
| Iterative | 33 | 29 | 0 | 12 | 12 |
| Shuffled | 44 | 4 | 0 | 4 | 4 |
| Upfront | 22 | 1 | 0 | 1 | 1 |
| Sequential | 19 | 0 | 0 | 0 | 0 |

Six of random's 24 successful runs found only flagged acceptable compounds;
18 also found an unflagged acceptable candidate. Thus the flagged compounds
account for some successful random trajectories, but their presence cannot
account for the whole observed advantage. **18 versus 12 is a post-hoc
descriptive partition, not a replacement endpoint or a new inferential test.**
It is not the outcome of rerunning either strategy on a restricted pool.

The similar total hit counts, 29 versus 33, hide different distributions:
iterative's hits cluster in twelve runs; random spreads them over 24. Ten of
the twelve successful iterative runs first succeed at queries 8–10. Of its
29 acceptable picks, 28 occur at queries 6–10, and 26 are LiAlSiO4 polymorphs.
That supports delayed adaptation and narrow exploration. It does not show
that additional budget would necessarily close the gap. Repeated picks within
a run are not independent experimental replicates.

A limited keyword check of the recorded proposal hypotheses/motivations
finds no mentions of perchlorate, iodate, periodate, oxidiser/oxidizer,
hazard or explosion stems in any LLZO LLM arm. This does not establish the
absence of all safety reasoning; it prevents attributing deliberate hazard
avoidance to the model on the available evidence.

## Correct the explanation of why the proxy admits them

Avoid “fully oxidised anions have nothing left to react with.” Oxidisers can
be reduced, and an oxyanion can decompose while releasing oxygen. More
specifically, our evaluator includes coating self-decomposition and oxygen
phases. The archived LiClO4–LLZO contact explicitly lists **O2** among its
products, alongside La(ClO4)3 and La2Zr2O7.

The objective measures additional reaction relative to separately equilibrated
reactants, together with coating self-decomposition and a band-gap gate.
“Acceptable” therefore does not require an intact stack or forbid gas products.
LiClO4's self-decomposition penalty is zero in the cached model; its additional
LLZO contact penalty is 0.01279 eV/non-Li atom, below 0.050.

An additional offline diagnostic uses the pinned LiClO4 entry and the lowest
cached corrected LiCl and elemental oxygen energies. For
`LiClO4 -> LiCl + 2 O2`, the energy difference is **+1.77425 eV/formula** in
this entry set. The Li inventory is unchanged, so the lithium chemical
potential cancels: setting 4 V alone cannot explain the sign. The diagnostic
is not a finite-temperature prediction or proof of which model approximation
causes the discrepancy with practical thermal behaviour.

The supported limitation is that this 0 K thermodynamic compatibility proxy
does not qualify processing/operating-temperature stability, gas free energies
at specified conditions, handling hazards, transport or practical coating
performance. Do not turn a caveat into a post-hoc exemption from the benchmark
result, or imply that all other acceptable candidates are validated.

## Suggested slide language and next steps

> In LLZO, feedback improves selection over the sequential policy, but random
> exploration finds benchmark-acceptable candidates more often within ten
> queries. Iterative selections adapt late and concentrate on aluminosilicates.
> The thermodynamic criterion admits oxyhalogen compounds requiring separate
> practical review; benchmark acceptance is not coating qualification.

Keep the primary Holm results: iterative beats sequential in LLZO; its
contrast with shuffled is not significant after correction. A narrow prior
misaligned with the criterion is a plausible interpretation, not a proven
causal mechanism or demonstrated safety judgement. We should not say the
LLM ought to have proposed perchlorate, nor that its loss is thereby invalid.

Add the five-ID annotation and the descriptive 18/30 versus 12/30 partition
in a backup slide or notes. Preserve the frozen pool, criterion and primary
analysis. A future practically filtered pool would be a separately declared
experiment, with new baselines; it is not needed to finish this study.

## Reproduction

`scripts/audit_llzo_chemistry.py` checks the benchmark/dataset digests and all
150 archived run-file hashes, then recounts selections and the diagnostic
reaction. It uses no network or provider credentials. After retrieving the
production archive from Adem's branch, run from the repository root:

```sh
.venv/bin/python scripts/audit_llzo_chemistry.py \
  --experiment /path/to/environment_v1/llzo \
  --output data/reviews/llzo_chemistry_audit_20261021.json
```

The saved JSON contains the exact IDs, flag evidence, hashes, per-run counts,
first-hit positions, formula counts, frozen reaction products and diagnostic
entry energies. Frozen benchmark digest:
`9bdef5811bafc0b24f6ae55140f74f0be592a0f4367ca253310e0544ebb8e060`.
No PowerPoint slides or primary experiment files were edited in this audit.
