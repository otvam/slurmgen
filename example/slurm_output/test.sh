#!/bin/bash

# ############### Bash commands
set -e error
set -o nounset
set -o pipefail

# ############### Slurm commands
#SBATCH --job-name="test"
#SBATCH --output="slurm_output/test.log"
#SBATCH --time="4:00:00"
#SBATCH --nodes="1"
#SBATCH --ntasks-per-node="2"
#SBATCH --mem="8G"

# ############### environment variables
export PYTHONUNBUFFERED="1"
export VARWORLD="Welcome to everyone"

echo "================================== test - `date -u +"%D %H:%M:%S"`"

echo "==================== PARAM"
echo "JOB TAG      : test"
echo "HOSTNAME     : $HOSTNAME"

echo "==================== TIME"
echo "DATE GEN     : `date -u +"%D : %H:%M:%S" -d @1726849091`"
echo "DATE RUN     : `date -u +"%D : %H:%M:%S" -d @$(date -u +%s)`"

echo "==================== SLURM"
echo "JOB ID       : $SLURM_JOB_ID"
echo "JOB NAME     : $SLURM_JOB_NAME"
echo "JOB NODE     : $SLURM_JOB_NODELIST"

echo "==================== RUN: version"
python3 --version

echo "==================== RUN: hello"
python3 run_slurm.py "hello" "hello world!"

echo "==================== RUN: goodbye"
python3 run_slurm.py "goodbye" "goodbye world!"

echo "================================== test - `date -u +"%D %H:%M:%S"`"

# ############### exit script
exit 0
