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
params = {
    "log_lsun": row.log_lsun,
    "t_exp": row.t_exp * u.day,
    "t_inner": row.t_inner * u.K,
    "v_start": row.v_start * u.km/u.s
}

set_output_dir('/u/ml168/scratch/grid_output')

# Write data if successful
try:
    print('\n' + 'STARTING RUN #' + str(index) + '\n')
    run_tardis(params, output_name, index)
    write_data(params, output_name)
except Exception as e:
    print('Error:', e)