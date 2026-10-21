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
