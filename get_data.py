from param_space import utilities, functions
from param_space.run_tardis import run_tardis_test
import astropy.units as u

data = {
    "log_lsun": 9.398,
    "t_exp": 11 * u.day,
    "t_inner": 16000 * u.K,
    "v_start": utilities.guess_v_start
}

functions.step_through_space_extrema(run_tardis_test, "run_data.log", data)