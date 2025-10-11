from param_space.run_tardis import run_tardis
from param_space.functions import write_data, set_output_dir
import astropy.units as u
import pandas as pd
import sys
import os

output_name = '2020jfo'
grid_name = 'grid.csv'

# Read grid
current_dir = os.path.dirname(os.path.abspath(__file__))
grid_dir = os.path.join(current_dir, grid_name)
df = pd.read_csv(grid_dir)

# Find specified grid entry
index = int(sys.argv[1])
row = df.iloc[index]

# Add on units
units = {
    't_exp': u.day,
    't_inner': u.K,
    'v_start': u.km/u.s
}
for name, value in row.items():
    if units[name]:
        row[name] = value * units[name]

# Convert to correct format
params = row.to_dict()

# Write data if successful
set_output_dir('/u/ml168/scratch/grid_output')
try:
    print('\n' + 'STARTING RUN #' + str(index) + '\n')
    run_tardis(params, output_name, index)
    write_data(params, output_name)
except Exception as e:
    print('Error:', e)