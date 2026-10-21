# Niflheim compute — access and status

User-authorized on 21 October 2026 for heavier interphAIse calculations.

- SSH alias: `fjorm`; verified hostname: `fjorm.fysik.dtu.dk`.
- Working directory: `/home/scratch12/davti/OSI_Hackathon`.
- SSH batch-mode access succeeded. The directory exists and was empty at inspection.
- `sbatch`, `squeue`, `sinfo` and `rsync` are available.
- Slurm advertises CPU partitions and GPU partitions including `a100`, `a100el9`,
  `h200el9` and RTX3090 partitions. Availability in `sinfo` does not establish this
  account's allocation entitlement or a validated submission configuration.
- Default `python3` is **3.9.25**; this project requires Python >=3.11. Prepare a
  separate compatible environment before running the workflow. No environment was
  installed, no project files were transferred and no jobs were submitted in this check.

## Next setup for a heavier run

1. Inspect available Python/CUDA modules and account/partition constraints; choose
   a supported Python environment and a suitable Slurm resource request.
2. Transfer a pinned code revision, explicit input structures and the PET-MAD S
   1.6.0 checkpoint. Verify its hash against `PETMAD_INTERFACE_PILOT.md`. Do not copy
   the local macOS virtual environment or `.env`.
3. Make the pilot runner's device/thread selection configurable: it currently fixes
   CPU and two Torch threads. Validate a small calculation within an allocation
   before using GPU execution for production runs.
4. Submit heavier relaxations under Slurm, keeping outputs in unique run directories
   beneath the authorized scratch directory. Do not run heavy work on the login node.
5. Retrieve compact results, structures, logs and scheduler accounting. Record the
   code revision, model hash, environment, job IDs, resources, convergence and wall time.

The existing local pilot remains the initial reference. Cluster access is verified;
PET-MAD cluster execution and GPU behavior are not yet validated. Do not interfere
with unrelated jobs already running under the account.

## Verified setup — 21 October 2026 (evening)

The user re-authorised heavier runs and named both login hosts, `ssh fjorm` and `ssh thul`
(both Rocky Linux 9.8). The user also asked for their miniforge install to be used.

- **Environment:** an isolated conda env at
  `/home/scratch12/davti/OSI_Hackathon/envs/interphaise` (`source ~/miniforge3/bin/activate;
  conda activate <path>`). Python 3.12 with the local pins (torch 2.14.1+cu130, upet 0.3.1,
  ASE 3.29.0, pymatgen 2026.9.24, numpy 2.5.4, metatomic-torch 0.1.19), installed with
  `pip -c constraints.txt -e code[upet,dev]`. The freeze is archived in
  `data/petmad/niflheim_smoke_v1/interphaise_freeze.txt`. The user's other conda envs
  (`upet`, `pet-mad`, …) were not used or modified.
- **Code and model:** `git archive <commit>` into `code_<commit>/` with a `COMMIT` file;
  `code` is a symlink to the current snapshot. The checkpoint is `models/pet-mad-s-v1.6.0.ckpt`,
  SHA-256 verified `3f52e97c…`. No `.env` or credentials on the cluster.
- **Jobs:** `scripts/niflheim/run_interface.sbatch`. **Niflheim rejects batch scripts with
  more than 10 arguments**, so runner arguments go in `--export=ALL,RUN_ARGS="..."`.
  Use EL9 partitions: GPU `sm3090el9_devel` (4 h) or `sm3090el9`; CPU `xeon24el9`
  with `--exclusive`.
- **Smoke test** (code `ea02e86`): the archived 504-atom cathode run
  (`cathode_thickness_v1/build_F2`, 0.34 fraction, registry (0,0,2 Å)) was reproduced on
  both devices. Same step counts (59 / 43 / 24) and 144 calls on both.

| Device | Job | W_adh (J/m²) | Δ vs local 3.479353 | Wall |
|---|---|---:|---:|---:|
| RTX 3090 (s001, driver 595.104.02), 4 CPUs | 11013629 | 3.479507 | +1.5×10⁻⁴ | 37 s |
| xeon24el9 (x180), 24 cores, exclusive | 11013630 | 3.479287 | −6.6×10⁻⁵ | 90 s |
| Local Mac, 4 threads (archived) | — | 3.479353 | — | 138 s |

The differences are float noise. GPU execution is validated for this workflow. Evidence:
`data/petmad/niflheim_smoke_v1/`. Pending jobs not belonging to this project were left
untouched. SSH use is kept to single batched calls (fail2ban).
