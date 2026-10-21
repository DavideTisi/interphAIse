#!/bin/bash
# One run_petmad_interface.py calculation under Slurm on Niflheim (EL9 partitions).
# Niflheim allows at most 10 script arguments, so pass the runner arguments in RUN_ARGS:
#   sbatch --partition=sm3090el9_devel --gres=gpu:1 --cpus-per-task=4 --time=01:00:00 \
#     --job-name=iface --export=ALL,RUN_ARGS="--device cuda --input <build dir> \
#     --output <fresh run dir> --fixed-depth 3.257602 --registry 0 0 2.0" scripts/niflheim/run_interface.sbatch
# CPU: --partition=xeon24el9 --nodes=1 --ntasks=1 --cpus-per-task=24 --exclusive and --device cpu.
#SBATCH --output=logs/%x-%j.out
#SBATCH --nodes=1
#SBATCH --ntasks=1
set -eo pipefail
source /etc/profile
ROOT=/home/scratch12/davti/OSI_Hackathon
CODE=${CODE:-$ROOT/code}
source ~/miniforge3/bin/activate
conda activate $ROOT/envs/interphaise
export HF_HUB_OFFLINE=1 MPLCONFIGDIR=${TMPDIR:-/tmp}/mpl-$SLURM_JOB_ID OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
cd $CODE
# Provenance for the job, written next to the run outputs by the caller's --output.
echo "job=$SLURM_JOB_ID node=$(hostname) partition=$SLURM_JOB_PARTITION cpus=${SLURM_CPUS_PER_TASK:-1} gpus=${CUDA_VISIBLE_DEVICES:-none} code=$(cat $CODE/COMMIT 2>/dev/null || echo unknown)"
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null || true
python scripts/run_petmad_interface.py --checkpoint $ROOT/models/pet-mad-s-v1.6.0.ckpt --threads ${SLURM_CPUS_PER_TASK:-1} $RUN_ARGS "$@"
# Optional: fixed-geometry separation of the finished run, on the same device (SEPARATE=<run dir>).
if [ -n "$SEPARATE" ]; then
    python scripts/fixed_geometry_separation.py "$SEPARATE" --checkpoint $ROOT/models/pet-mad-s-v1.6.0.ckpt \
        --threads ${SLURM_CPUS_PER_TASK:-1} --device ${SEP_DEVICE:-cpu}
fi
