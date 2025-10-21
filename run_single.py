from param_space.run_tardis import run_tardis
from param_space.functions import write_data, set_output_dir, set_folder_name
import astropy.units as u
import pandas as pd

set_output_dir('/u/ml168/scratch')
set_folder_name('single')
params = {
    'log_lsun': 10.006166,
    't_exp': 13.356523 * u.day,
    't_inner': 11888.77105 * u.K,
    'v_start': 5879.888876 * u.km/u.s
}

try:
    run_tardis(params)
    write_data(params)
except Exception as e:
    print('Error:', e)