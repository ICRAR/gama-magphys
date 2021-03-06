#!/bin/bash --login
# SLURM directives
#
#SBATCH --job-name=gama-magphys
#SBATCH --account=partner1024
#SBATCH --time=03:00:00
#SBATCH --ntasks=24
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --array=0-31

# with the node=1 this will run 24 versions of gama-magphys on the same one
aprun -n 24 -N 24 $SLURM_SUBMIT_DIR/gama-magphys-ned.sh
