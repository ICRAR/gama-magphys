#!/bin/bash --login

# SLURM directives
#
# Here we specify to SLURM we want one node (--nodes=1) with
# a wall-clock time limit of ten minutes (--time=00:10:00).

#SBATCH --nodes=1
#SBATCH --time=01:00:00
#SBATCH --account=partner1024

aprun -n 1 bash ~/test.sh
