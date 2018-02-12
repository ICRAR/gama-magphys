#!/bin/bash

# We are one of 24 running on a node as part of an array job
# Show the environment variables
echo "ALPS_APP_PE = $ALPS_APP_PE"
echo "SLURM_ARRAY_TASK_ID = $SLURM_ARRAY_TASK_ID"
echo "SLURM_SUBMIT_DIR = $SLURM_SUBMIT_DIR"

dir_id=`printf %06d $((SLURM_ARRAY_TASK_ID * 24 + ALPS_APP_PE))`
echo "dir_id = $dir_id"
directory="/scratch/pawsey0160/kvinsen/run13_gama_2017_01_19/$dir_id"
echo "directory = $directory"
if [ -d $directory ]; then
    cd $directory
    date > "$SLURM_SUBMIT_DIR/$dir_id.log"
    bash process_data.sh >> "$SLURM_SUBMIT_DIR/$dir_id.log"
    date >> "$SLURM_SUBMIT_DIR/$dir_id.log"
    echo "Completed directory = $directory at `date`"
else
    echo "Could not find directory = $directory"
fi
