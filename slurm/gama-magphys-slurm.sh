#!/bin/bash --login
# SLURM directives
#
#SBATCH --job-name=gama-magphys
#SBATCH --account=partner1024
#SBATCH --time=18:00:00
#SBATCH --ntasks=24
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1

aprun -n 24 -N 24 $SLURM_SUBMIT_DIR/gama-magphys.sh

date
wait
date
