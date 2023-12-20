#!/bin/bash

#SBATCH --job-name="test"
#SBATCH --output="slurm_output/test.log"
#SBATCH --time="4:00:00"
#SBATCH --nodes="1"
#SBATCH --ntasks-per-node="2"
#SBATCH --mem="8G"

echo "================================== test - `date -u +"%D %H:%M:%S"`"

echo "==================== PARAM"
echo "JOB TAG      : test"
echo "LOG FILE     : slurm_output/test.log"
echo "SCRIPT FILE  : slurm_output/test.sh"

echo "==================== TIME"
echo "DATE GEN     : 12/20/23 14:16:35"
echo "DATE RUN     : `date -u +"%D %H:%M:%S"`"

echo "==================== SLURM"
echo "JOB ID       : $SLURM_JOB_ID"
echo "JOB NAME     : $SLURM_JOB_NAME"
echo "JOB NODE     : $SLURM_JOB_NODELIST"

echo "==================== ENV VAR"
export PYTHONUNBUFFERED="1"
export VARWORLD="Welcome to everyone!"

echo "==================== RUN: version"
python3 "--version"

echo "==================== RUN: hello"
python3 "run_slurm.py" "hello" "hello world!"

echo "==================== RUN: goodbye"
python3 "run_slurm.py" "goodbye" "goodbye world!"

echo "================================== test - `date -u +"%D %H:%M:%S"`"

exit 0
