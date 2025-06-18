from param_space.run_tardis import run_tardis
import astropy.units as u

params = {
    "log_lsun": 9.398,
    "t_exp": 11 * u.day,
    "t_inner": 16000 * u.K,
    "v_start": 8912 * u.km/u.s
}

run_tardis(params)