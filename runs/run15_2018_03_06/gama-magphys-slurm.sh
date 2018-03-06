#!/bin/bash --login
# SLURM directives
#
#SBATCH --job-name=gama-magphys
#SBATCH --time=04:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --nodes=1
#SBATCH --array=0-1994%20

module load gfortran

cd /scratch/kevin/gama/run15_2018_03_06/`printf %06d ${SLURM_ARRAY_TASK_ID}`
bash process_data.sh
