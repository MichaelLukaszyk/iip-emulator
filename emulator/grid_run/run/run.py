from emulator.grid_run.run_tardis import run_tardis
from emulator.grid_run.output import get_folder_dir, set_output_dir, set_folder_name
import astropy.units as u
import pandas as pd
import shutil
import sys
import os

# Settings
set_output_dir('/u/ml168/scratch')
set_folder_name('grid_run')

# Copy grid
current_dir = os.path.dirname(os.path.abspath(__file__))
grid_out_path = os.path.join(get_folder_dir(), 'grid.csv')
grid_in_path = os.path.join(current_dir, 'grid.csv')
if not os.path.isfile(grid_out_path):
    shutil.copyfile(grid_in_path, grid_out_path)

# Copy config
config_out_path = os.path.join(get_folder_dir(), 'base_config.yml')
config_in_path = os.path.join(current_dir, '../tardis_data/base_config.yml')
if not os.path.isfile(config_out_path):
    shutil.copyfile(config_in_path, config_out_path)

index = int(sys.argv[1])

if index == -1:
    print('Initialization complete, you may proceed to submit the batch job.')
else:
    # Find specified grid entry
    df = pd.read_csv(grid_in_path)
    row = df.iloc[index]
    params = row.to_dict()
    params['id'] = int(params['id'])

    # Write data if successful
    try:
        print('\n' + 'STARTING ID #' + str(params['id']) + '\n')
        run_tardis(params)
    except Exception as e:
        print('Error:', e)