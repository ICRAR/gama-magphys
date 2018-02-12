#!/bin/sh
# SLURM directives
#
#SBATCH --job-name=slurm_test
#SBATCH --account=pawsey0160
#SBATCH --time=01:00:00
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --array=0-2

cd $SLURM_SUBMIT_DIR

srun run-task.sh
