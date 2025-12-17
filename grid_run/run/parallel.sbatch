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
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
#SBATCH --time=8:00:00

#SBATCH --array=0-999%100

START=$(( SLURM_ARRAY_TASK_ID * 5 ))
END=$(( START + 4 ))

for (( i=$START; i<=$END; i++ )); do
    python ~/iip-emulator/grid_run/run/run.py $i
done