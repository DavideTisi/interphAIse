"""MLIP loader.

Prefixes:
  upet:<model>@<version>    Explicit UPET family and checkpoint, e.g.
                             upet:pet-mad-s@1.6.0 (r2SCAN).
  pet-mad[-<version>]        Legacy PET-MAD (PBEsol, non-spin-polarised). Good for
                             sulfides/halides/Li metal; be careful with magnetic
                             TM-oxide cathodes (NMC, LFP).
  metatomic:<path.pt>        any exported metatomic model, e.g. a PET-MAD
                             fine-tune for Li6PS5Cl.
  mace-mp-*, uma-*, esen-*   delegated to HELLMM's loader if installed
                             (mace-mp is trained on MPtrj, PBE+U).
  lj                         Lennard-Jones toy calculator for offline smoke
                             tests of the plumbing — numbers are meaningless.
"""

from __future__ import annotations


def best_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"


def load_mlip(model: str, device: str | None = None):
    if device is None:
        device = best_device()
        # Use CPU on Apple hardware unless MPS was explicitly requested.
        if model.startswith("upet:") and device == "mps":
            device = "cpu"

    if model == "lj":
        from ase.calculators.lj import LennardJones

        return LennardJones(sigma=2.0, epsilon=0.05, rc=6.0, smooth=True)

    if model.startswith("upet:"):
        specification = model[len("upet:"):]
        name, separator, version = specification.partition("@")
        if not separator or not name or not version or "@" in version or version == "latest":
            raise ValueError("Use an explicit UPET checkpoint: upet:<model>@<version>")
        from upet.ase import UPETCalculator

        return UPETCalculator(model=name, version=version, device=device)

    if model.startswith("pet-mad"):
        from pet_mad.calculator import PETMADCalculator  # pip install pet-mad

        version = model[len("pet-mad-"):] if model.startswith("pet-mad-") else "latest"
        return PETMADCalculator(version=version, device=device)

    if model.startswith("metatomic:"):
        from metatomic.torch.ase_calculator import MetatomicCalculator

        return MetatomicCalculator(model.split(":", 1)[1], device=device)

    try:
        from hellmm.tools.mlip import load_mlip as _hellmm_load  # type: ignore

        return _hellmm_load(model, device=device)
    except ImportError:
        pass

    if model.startswith("mace-mp"):
        from mace.calculators import mace_mp

        name = model[len("mace-mp-"):] if model != "mace-mp" else "medium"
        dtype = "float32" if device == "mps" else "float64"
        return mace_mp(model=name, device=device, default_dtype=dtype)

    raise ValueError(f"Unknown MLIP '{model}'")
