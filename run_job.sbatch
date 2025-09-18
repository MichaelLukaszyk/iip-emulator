#!/bin/bash
#SBATCH --job-name=single_test
#SBATCH --array=0-2
#SBATCH --output=/u/ml168/scratch/grid_run_%A.out
#SBATCH --error=/u/ml168/scratch/grid_run_%A.err
#SBATCH --mail-user=ml168@illinois.edu
#SBATCH --mail-type=FAIL
#SBATCH --partition=caps
#SBATCH --account=caps
#SBATCH --cpus-per-task=4
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --mem=80G
#SBATCH --time=01:00:00

module load anaconda3
conda activate tardis
python run_grid.py $SLURM_ARRAY_TASK_ID