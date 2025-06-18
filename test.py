from param_space.run_tardis import run_tardis
from param_space.functions import write_data
import astropy.units as u

params = {
    "log_lsun": 9.398,
    "t_exp": 11 * u.day,
    "t_inner": 16000 * u.K,
    "v_start": 7092 * u.km/u.s
}

run_tardis(params)
write_data("test_data.log", params)