from param_space.run_tardis import run_tardis
from param_space.functions import write_data
import astropy.units as u
import pandas as pd
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
grid_dir = os.path.join(current_dir, 'grid.csv')
df = pd.read_csv(grid_dir)

arg = int(sys.argv[1])
row = df.iloc[arg]
params = {
    "log_lsun": row.log_lsun,
    "t_exp": row.t_exp * u.day,
    "t_inner": row.t_inner * u.K,
    "v_start": row.v_start * u.km/u.s
}

run_tardis(params, row.index)
write_data(f"test_data{arg}.log", params)