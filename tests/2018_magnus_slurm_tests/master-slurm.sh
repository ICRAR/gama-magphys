#!/bin/sh
# SLURM directives
#
#SBATCH --job-name=slurm_test
#SBATCH --account=pawsey0160
#SBATCH --time=01:00:00
#SBATCH --ntasks=24
#SBATCH --ntasks-per-node=24
#SBATCH --nodes=1
#SBATCH --array=0-2

echo SBATCH_MEM_BIND             = $SBATCH_MEM_BIND
echo SBATCH_MEM_BIND_LIST        = $SBATCH_MEM_BIND_LIST
echo SBATCH_MEM_BIND_PREFER      = $SBATCH_MEM_BIND_PREFER
echo SBATCH_MEM_BIND_TYPE        = $SBATCH_MEM_BIND_TYPE
echo SBATCH_MEM_BIND_VERBOSE     = $SBATCH_MEM_BIND_VERBOSE
#echo SLURM_*_PACK_GROUP_#        = $SLURM_*_PACK_GROUP_#
echo SLURM_ARRAY_TASK_COUNT      = $SLURM_ARRAY_TASK_COUNT
echo SLURM_ARRAY_TASK_ID         = $SLURM_ARRAY_TASK_ID
echo SLURM_ARRAY_TASK_MAX        = $SLURM_ARRAY_TASK_MAX
echo SLURM_ARRAY_TASK_MIN        = $SLURM_ARRAY_TASK_MIN
echo SLURM_ARRAY_TASK_STEP       = $SLURM_ARRAY_TASK_STEP
echo SLURM_ARRAY_JOB_ID          = $SLURM_ARRAY_JOB_ID
echo SLURM_CHECKPOINT_IMAGE_DIR  = $SLURM_CHECKPOINT_IMAGE_DIR
echo SLURM_CLUSTER_NAME          = $SLURM_CLUSTER_NAME
echo SLURM_CPUS_ON_NODE          = $SLURM_CPUS_ON_NODE
echo SLURM_CPUS_PER_TASK         = $SLURM_CPUS_PER_TASK
echo SLURM_DISTRIBUTION          = $SLURM_DISTRIBUTION
echo SLURM_GTIDS                 = $SLURM_GTIDS
echo SLURM_JOB_ACCOUNT           = $SLURM_JOB_ACCOUNT
echo SLURM_JOB_ID                = $SLURM_JOB_ID
echo SLURM_JOB_CPUS_PER_NODE     = $SLURM_JOB_CPUS_PER_NODE
echo SLURM_JOB_DEPENDENCY        = $SLURM_JOB_DEPENDENCY
echo SLURM_JOB_NAME              = $SLURM_JOB_NAME
echo SLURM_JOB_NODELIST          = $SLURM_JOB_NODELIST
echo SLURM_JOB_NUM_NODES         = $SLURM_JOB_NUM_NODES
echo SLURM_JOB_PARTITION         = $SLURM_JOB_PARTITION
echo SLURM_JOB_QOS               = $SLURM_JOB_QOS
echo SLURM_JOB_RESERVATION       = $SLURM_JOB_RESERVATION
echo SLURM_LOCALID               = $SLURM_LOCALID
echo SLURM_MEM_PER_CPU           = $SLURM_MEM_PER_CPU
echo SLURM_MEM_PER_NODE          = $SLURM_MEM_PER_NODE
echo SLURM_NODE_ALIASES          = $SLURM_NODE_ALIASES
echo SLURM_NODEID                = $SLURM_NODEID
echo SLURM_NTASKS                = $SLURM_NTASKS
echo SLURM_NTASKS_PER_CORE       = $SLURM_NTASKS_PER_CORE
echo SLURM_NTASKS_PER_NODE       = $SLURM_NTASKS_PER_NODE
echo SLURM_NTASKS_PER_SOCKET     = $SLURM_NTASKS_PER_SOCKET
echo SLURM_PACK_SIZE             = $SLURM_PACK_SIZE
echo SLURM_PRIO_PROCESS          = $SLURM_PRIO_PROCESS
echo SLURM_PROCID                = $SLURM_PROCID
echo SLURM_PROFILE               = $SLURM_PROFILE
echo SLURM_RESTART_COUNT         = $SLURM_RESTART_COUNT
echo SLURM_STEP_ID               = $SLURM_STEP_ID
echo SLURM_SUBMIT_DIR            = $SLURM_SUBMIT_DIR
echo SLURM_SUBMIT_HOST           = $SLURM_SUBMIT_HOST
echo SLURM_TASKS_PER_NODE        = $SLURM_TASKS_PER_NODE
echo SLURM_TASK_PID              = $SLURM_TASK_PID
echo SLURM_TOPOLOGY_ADDR         = $SLURM_TOPOLOGY_ADDR
echo SLURM_TOPOLOGY_ADDR_PATTERN = $SLURM_TOPOLOGY_ADDR_PATTERN
echo SLURMD_NODENAME             = $SLURMD_NODENAME

cd $SLURM_SUBMIT_DIR

/bin/bash run-task.sh

