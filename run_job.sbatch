#!/bin/bash
#SBATCH --job-name=single_test
#SBATCH --time=01:00:00
#SBATCH --partition=caps
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=80G
#SBATCH --account=caps
#SBATCH --array=0-2
#SBATCH --output=/scratch/mikel/grid_run_%A.out
#SBATCH --error=/scratch/mikel/grid_run_%A.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ml168@illinois.edu
#SBATCH --cpus-per-task=4

module load anaconda3
conda activate tardis
python run_grid.py $SLURM_ARRAY_TASK_ID