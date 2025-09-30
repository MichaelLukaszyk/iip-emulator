#!/bin/bash
#SBATCH --job-name=grid_run
#SBATCH --array=0-499
#SBATCH --output=/u/ml168/scratch/grid_run_%A.out
#SBATCH --error=/u/ml168/scratch/grid_run_%A.err
#SBATCH --mail-user=ml168@illinois.edu
#SBATCH --mail-type=FAIL
#SBATCH --partition=caps
#SBATCH --account=caps
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=80G
#SBATCH --time=24:00:00

python run_grid.py $SLURM_ARRAY_TASK_ID