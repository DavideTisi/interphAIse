"""Central configuration (same pattern as HELLMM's config.py)."""

from interphaise.context import InterfaceContext
from interphaise.screen import ScreenConfig

# LLM: a HELLMM alias if hellmm is installed, otherwise a litellm model string.
# Default: direct Anthropic Claude Haiku 5.5, billed on MY_ANTHROPIC_KEY (see
# interphaise/llm.py / scripts/check_anthropic_key.py).
LLM_MODEL = "anthropic/claude-haiku-5-5"   # or "deepseek-v3.2" / "openrouter/deepseek/deepseek-v3.2"

# Explicit checkpoint for reproducible MLIP evaluations: PET-MAD S 1.6.0 (r2SCAN).
# Keep MLIP energy differences separate from Materials Project thermodynamics.
MLIP_ANODE = "upet:pet-mad-s@1.6.0"
MLIP_CATHODE = "upet:pet-mad-s@1.6.0"

N_RUNS = 3          # consensus samples per LLM decision
MAX_RETRIES = 2     # per branch point

CASES: list[InterfaceContext] = [
    # Validation case: stable (kinetically) interface with literature W_adh values.
    InterfaceContext(electrode="Li", electrolyte="Li7La3Zr2O12", role="anode", voltage=0.0, max_atoms=800),
    # Reactive case: thermodynamics says Li2S + Li3P + LiCl; the demo of the interphase branch.
    InterfaceContext(electrode="Li", electrolyte="Li6PS5Cl", role="anode", voltage=0.0),
    # Cathode case: voltage-dependent stability window.
    InterfaceContext(electrode="LiCoO2", electrolyte="Li6PS5Cl", role="cathode", voltage=4.0),
]

# ---------------------------------------------------------------------------
# Flagship: which buffer coating stabilises LiCoO2 | Li6PS5Cl at 4 V?
# Oxide coatings used in sulfide all-solid-state cells, plus a halide.
# Check the MP polymorph picked for each (or pin it in coating_mp_ids).
# ---------------------------------------------------------------------------
COATING_SCREEN = ScreenConfig(
    electrode="LiCoO2",
    electrolyte="Li6PS5Cl",
    voltage=4.0,
    role="cathode",
    coatings=["LiNbO3", "Li3PO4", "Li2ZrO3", "LiTaO3", "Li3BO3", "Li3InCl6"],
    include_uncoated=True,
)
