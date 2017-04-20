#!/bin/bash --login
# SLURM directives
#
#SBATCH --job-name=gama-magphys
#SBATCH --account=pawsey0160
#SBATCH --time=03:00:00
#SBATCH --ntasks=24
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --array=0-22

# with the node=1 this will run 24 versions of gama-magphys on the same one
aprun -n 24 -N 24 $SLURM_SUBMIT_DIR/gama-magphys.sh
