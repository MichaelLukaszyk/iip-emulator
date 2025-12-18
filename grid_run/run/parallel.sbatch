#!/bin/bash
#SBATCH --job-name=grid_run
#SBATCH --output=/u/ml168/scratch/%A_%a.log
#SBATCH --error=/u/ml168/scratch/%A_%a.log
#SBATCH --mail-user=ml168@illinois.edu
#SBATCH --mail-type=FAIL
#SBATCH --partition=caps
#SBATCH --account=caps

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=20G
#SBATCH --time=20:00:00

#SBATCH --array=0-999%100

START=$(( SLURM_ARRAY_TASK_ID * 10 ))
END=$(( START + 9 ))

for (( i=$START; i<=$END; i++ )); do
    python ~/iip-emulator/grid_run/run/run.py $i
done