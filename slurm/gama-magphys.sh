#!/bin/bash --login

# SLURM directives
#
# Here we specify to SLURM we want one node (--nodes=1) with
# a wall-clock time limit of ten minutes (--time=00:10:00).

#SBATCH --nodes=1
#SBATCH --time=18:00:00
#SBATCH --account=partner1024
#SBATCH --array=0-2

# Launch twenty-four independent copies of a single application.
#
# Executution is controlled by standard bash scripting which
# generates a list 0, 1,..., 23
#
# We use "aprun -n 1 -cc $jobnumber" to control the placement of each
# serial instance of the application. It is assumed the application
# takes the input file name as a command line argument. Output
# is redirected to the numbered output directory.
#
# The ampersand "&" at the end of each aprun line is required and allows
# concurrent execution. The "wait" is also required and ensures
# all instances of aprun (and hence the application) have completed
# before exiting.

for jobnumber in `seq 0 23`
do
    dir_id=$((SLURM_ARRAY_TASK_ID * 24 + jobnumber))
    directory=/group/partner1024/kvinsen/gama-magphys-data/run_2015_01/`printf %06d ${dir_id}`

    if [ -f ${directory} ]; then
        cd ${directory}
        aprun -n 1 -cc ${jobnumber} bash process_data.sh > ${dir_id}.log &
    fi
done

wait
