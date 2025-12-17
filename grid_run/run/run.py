import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grid_run.run_tardis import run_tardis
from grid_run.functions import write_data, get_folder_dir, set_output_dir, set_folder_name
import astropy.units as u
import pandas as pd

# Before running:
# 1. Ensure base_config in grid_run.tardis_data is correct
# 2. Make changes to make_csvy if shell structure / abundances changes are needed
# 3. Create grid.csv file in this run directory
# 4. Ensure settings below are correct
# 5. Update sbatch script to match grid length
# 6. Run sbatch script with tardis conda environment active

# Settings
set_output_dir('/u/ml168/scratch')
set_folder_name('5000_runs')
grid_name = 'grid.csv'
units = {
    'lum': u.erg/u.s,
    't_exp': u.day,
    't_inner': u.K,
    'v_start': u.km/u.s
}

# Read grid
current_dir = os.path.dirname(os.path.abspath(__file__))
grid_dir = os.path.join(current_dir, grid_name)
df = pd.read_csv(grid_dir)
df.to_csv(os.path.join(get_folder_dir(), 'grid.csv'), index=False)

# Find specified grid entry
index = int(sys.argv[1])
row = df.iloc[index]

# Add on units
params = {}
for name, value in row.items():
    if name in units:
        params[name] = value * units[name]
    else:
        params[name] = value

# Write data if successful
try:
    print('\n' + 'STARTING RUN #' + str(index) + '\n')
    run_tardis(params, index)
    write_data(params)
except Exception as e:
    print('Error:', e)