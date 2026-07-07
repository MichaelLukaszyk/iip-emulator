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
#SBATCH --mem=50G
#SBATCH --time=20:00:00

START=$(( SLURM_ARRAY_TASK_ID * 10 ))
END=$(( START + 9 ))
MAX_INDEX=$(($(wc -l < grid.csv) - 2))

for (( i=START; i<=END && i<=MAX_INDEX; i++ )); do
    python ~/iip-emulator/emulator/grid_run/run/run.py $i
done