#!/bin/bash

echo "ALPS_APP_PE = $ALPS_APP_PE"
echo "SLURM_ARRAY_TASK_ID = $SLURM_ARRAY_TASK_ID"
echo "SLURM_SUBMIT_DIR = $SLURM_SUBMIT_DIR"

SLURM_ARRAY_TASK_ID=0
dir_id=`printf %06d $((SLURM_ARRAY_TASK_ID * 24 + ALPS_APP_PE))`
echo "dir_id = $dir_id"
directory="/group/partner1024/kvinsen/gama-magphys-data/run_02-2015_02/$dir_id"
echo "directory = $directory"
if [ -d $directory ]; then
    cd $directory
    bash process_data.sh > "$SLURM_SUBMIT_DIR/$dir_id.log" &
fi
