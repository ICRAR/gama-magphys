#!/bin/bash

JOB_ONE=$(sbatch master-slurm.sh)

echo JOB_ONE       = $JOB_ONE
echo SLURM_JOB_ID  = $SLURM_JOB_ID

JOB_TWO=$(sbatch --dependency=afterok:$SLURM_JOB_ID master-slurm.sh)

echo JOB_TWO       = $JOB_TWO
echo SLURM_JOB_ID  = $SLURM_JOB_ID

