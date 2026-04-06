LINES=$(($(wc -l < grid.csv) - 1))
TASKS=$(((LINES + 9) / 10))

source activate tardis
python3 run.py -1
sbatch --array=0-$((TASKS - 1))%100 parallel.sbatch