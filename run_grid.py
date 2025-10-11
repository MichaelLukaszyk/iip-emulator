from param_space.run_tardis import run_tardis
from param_space.functions import write_data, set_output_dir, set_folder_name
import astropy.units as u
import pandas as pd
import sys
import os

set_output_dir('/u/ml168/scratch')
set_folder_name('noise_variation')
grid_name = 'grid.csv'
units = {
    't_exp': u.day,
    't_inner': u.K,
    'v_start': u.km/u.s
}

# Read grid
current_dir = os.path.dirname(os.path.abspath(__file__))
grid_dir = os.path.join(current_dir, grid_name)
df = pd.read_csv(grid_dir)

# Find specified grid entry
index = int(sys.argv[1])
row = df.iloc[index]

# Add on units
for name, value in row.items():
    if units[name]:
        row[name] = value * units[name]

# Convert to correct format
params = row.to_dict()

# Write data if successful
try:
    print('\n' + 'STARTING RUN #' + str(index) + '\n')
    run_tardis(params, index)
    write_data(params)
except Exception as e:
    print('Error:', e)