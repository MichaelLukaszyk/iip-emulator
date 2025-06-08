import astropy.units as u

step_config = {
    "log_lsun": {
        "step_size": 0.5,
        "min": 8,
        "max": 10.5
    },
    "t_exp": {
        "step_size": 0.5 * u.day,
        "min": 10 * u.day,
        "max": 12 * u.day
    },
    "v_start": {
        "step_size": 500 * u.km/u.s,
        "min": 4000 * u.km/u.s,
        "max": 12000 * u.km/u.s
    },
    "t_inner": {
        "step_size": 500 * u.K,
        "min": 5000 * u.K,
        "max": 25000 * u.K
    }
}

range_config = {
    "log_lsun": {
        "fail_range": 1.5,
        "converge_diff": 0.1,
        "step_up_size": 0.5,
        "step_down_size": None,
        "min": None,
        "max": None
    },
    "v_start": {
        "fail_range": 5000 * u.km/u.s,
        "converge_diff": 1000 * u.km/u.s,
        "step_up_size": 7500 * u.km/u.s,
        "step_down_size": 1000 * u.km/u.s,
        "min": 100 * u.km/u.s,
        "max": 25000 * u.km/u.s
    },
    "t_inner": {
        "fail_range": 4000 * u.K,
        "converge_diff": 1000 * u.K,
        "step_up_size": 30000 * u.K,
        "step_down_size": 4000 * u.K,
        "min": 500 * u.K,
        "max": 80000 * u.K
    }
}