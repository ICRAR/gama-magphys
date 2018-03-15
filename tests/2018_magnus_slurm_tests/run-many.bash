#!/bin/bash

JOB_ONE=$(sbatch --parsable master-slurm.sh)

echo JOB_ONE = $JOB_ONE

JOB_TWO=$(sbatch --dependency=afterok:$JOB_ONE --parsable master-slurm.sh)

echo JOB_TWO = $JOB_TWO
