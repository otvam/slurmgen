#!/bin/bash

# ############### Slurm commands
#SBATCH --job-name="test"
#SBATCH --output="slurm_output/test.log"
#SBATCH --time="4:00:00"
#SBATCH --nodes="1"
#SBATCH --ntasks-per-node="2"
#SBATCH --mem="8G"

# ############### init exit code
ret=0

# ############### environment variables
export PYTHONUNBUFFERED="1"
export VARWORLD="Welcome to everyone"

echo "================================== test - `date -u +"%D %H:%M:%S"`"

echo "==================== PARAM"
echo "JOB TAG      : test"
echo "HOSTNAME     : $HOSTNAME"

echo "==================== TIME"
echo "DATE GEN     : `date -u +"%D : %H:%M:%S" -d @1726845212`"
echo "DATE RUN     : `date -u +"%D : %H:%M:%S" -d @$(date -u +%s)`"

echo "==================== SLURM"
echo "JOB ID       : $SLURM_JOB_ID"
echo "JOB NAME     : $SLURM_JOB_NAME"
echo "JOB NODE     : $SLURM_JOB_NODELIST"

echo "==================== RUN: version"
python3 --version
ret=$(( ret || $? ))

echo "==================== RUN: hello"
python3 run_slurm.py "hello" "hello world!"
ret=$(( ret || $? ))

echo "==================== RUN: goodbye"
python3 run_slurm.py "goodbye" "goodbye world!"
ret=$(( ret || $? ))

echo "================================== test - `date -u +"%D %H:%M:%S"`"

# ############### exit with status
exit $ret
