import astropy.constants as c
import astropy.units as u
import numpy as np

def convert_quantities(data):
    if type(data) == dict:
        for key, value in data.items():
            if type(value) == u.Quantity:
                data[key] = str(value)
            elif type(value) == dict:
                convert_quantities(value)
    return data

def from_loglsun(log_lsun):
    return 10**log_lsun * c.L_sun

def to_loglsun(lum):
    return np.log10((lum / c.L_sun).to(u.dimensionless_unscaled))

def guess_v_start(params):
    L_1 = None
    if "lum" in params and type(params["lum"]) == u.Quantity:
        L_1 = params["lum"]
    elif "log_lsun" in params and type(params["log_lsun"]) == float:
        L_1 = from_loglsun(params["log_lsun"])
    
    L_0 = from_loglsun(9.398)
    v_0 = 8000 * u.km/u.s
    v_1 = np.sqrt((L_1 / L_0).to(u.dimensionless_unscaled)) * v_0
    return v_1

def guess_t_inner(params):
    L_1 = None
    if "lum" in params and type(params["lum"]) == u.Quantity:
        L_1 = params["lum"]
    elif "log_lsun" in params and type(params["log_lsun"]) == float:
        L_1 = from_loglsun(params["log_lsun"])

    L_0 = from_loglsun(9.398)
    T_0 = 18000 * u.K
    T_1 = np.sqrt((L_1 / L_0).to(u.dimensionless_unscaled)) * T_0
    return T_1