import astropy.constants as c
import astropy.units as u
import numpy as np

def from_loglsun(log_lsun):
    return 10**log_lsun * c.L_sun

def to_loglsun(lum):
    return np.log10((lum / c.L_sun).to(u.dimensionless_unscaled))

def guess_v_start_from_L(L_1):
    L_0 = from_loglsun(9.398)
    v_0 = 8000 * u.km/u.s
    v_1 = np.sqrt((L_1 / L_0).to(u.dimensionless_unscaled)) * v_0
    return v_1

def guess_t_inner_from_L(L_1):
    L_0 = from_loglsun(9.398)
    T_0 = 18000 * u.K
    T_1 = np.sqrt((L_1 / L_0).to(u.dimensionless_unscaled)) * T_0
    return T_1