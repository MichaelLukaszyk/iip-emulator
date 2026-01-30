import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from grid_run.run_tardis import run_tardis
from grid_run.functions import get_folder_dir, set_output_dir, set_folder_name
import astropy.units as u
import pandas as pd
import shutil

# Settings
set_output_dir('/u/ml168/scratch')
set_folder_name('grid_runs')
units = {
    'lum': u.erg/u.s,
    't_exp': u.day,
    't_inner': u.K,
    'v_start': u.km/u.s
}

# Copy grid and base config files
current_dir = os.path.dirname(os.path.abspath(__file__))
grid_out_path = os.path.join(get_folder_dir(), 'grid.csv')
grid_in_path = os.path.join(current_dir, 'grid.csv')
if not os.path.isfile(grid_out_path):
    shutil.copyfile(grid_in_path, grid_out_path)

config_out_path = os.path.join(get_folder_dir(), 'base_config.yml')
config_in_path = os.path.join(current_dir, '../tardis_data/base_config.yml')
if not os.path.isfile(config_out_path):
    shutil.copyfile(config_in_path, config_out_path)

# Find specified grid entry
df = pd.read_csv(grid_in_path)
index = int(sys.argv[1])
row = df.iloc[index]

# Add on units, copy over parameters
params = {}
for name, value in row.items():
    if name in units:
        params[name] = value * units[name]
    else:
        params[name] = value
params['id'] = int(params['id'])

# Write data if successful
try:
    print('\n' + 'STARTING ID #' + str(params['id']) + '\n')
    run_tardis(params)
except Exception as e:
    print('Error:', e)