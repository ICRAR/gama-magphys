#!/bin/sh
# SLURM directives
#
#SBATCH --job-name=slurm_test
#SBATCH --account=pawsey0160
#SBATCH --time=00:05:00
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --array=0-2
#SBATCH --parsable
#--SBATCH --partition=debugq

cd $SLURM_SUBMIT_DIR

srun run-task.sh
