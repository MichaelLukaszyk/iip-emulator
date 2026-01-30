LINES=$(($(wc -l < grid.csv) - 1))
TASKS=$(((LINES + 9) / 10))
conda activate tardis
sbatch --array=0-$((TASKS - 1))%100 parallel.sbatch