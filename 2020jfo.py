from param_space import utilities, functions
from param_space.run_tardis import run_tardis_test
import astropy.units as u

start_data = {
    "log_lsun": 9.398,
    "t_exp": 13 * u.day,
    "v_start": 7300 * u.km/u.s,
    "t_inner": 16000 * u.K,
}

step_config = {
    "log_lsun": {
        "step_size": 0.5,
        "min": 8,
        "max": 10.5
    },
    "t_exp": {
        "step_size": 0.5 * u.day,
        "min": 11 * u.day,
        "max": 15 * u.day
    },
    "v_start": {
        "step_size": 200 * u.km/u.s,
        "min": 6000 * u.km/u.s,
        "max": 8200 * u.km/u.s
    },
    "t_inner": {
        "step_size": 500 * u.K,
        "min": 5000 * u.K,
        "max": 25000 * u.K
    },
}

range_config = {
    "t_inner": {
        "fail_range": 4000 * u.K,
        "converge_diff": 1000 * u.K,
        "step_up_size": 30000 * u.K,
        "step_down_size": 4000 * u.K, # None to match step_up_size
        "min": 500 * u.K, # Supports None
        "max": 80000 * u.K # Supports None
    },
}

functions.step_through_space_extrema(run_tardis_test, "2020jfo.log", start_data, step_config, range_config)