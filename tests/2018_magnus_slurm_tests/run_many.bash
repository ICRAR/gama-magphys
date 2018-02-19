#!/bin/bash

JOB_ONE=$(sbatch master-slurm.sh)

echo JOB_ONE = $JOB_ONE

JOB_TWO=$(sbatch --dependency=afterok:$JOB_ONE master-slurm.sh)

echo JOB_TWO = $JOB_TWO
