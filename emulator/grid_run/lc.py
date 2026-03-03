from emulator.grid_run.run_tardis import set_threads, run_tardis
from emulator.interpolator.util import parse_runs_folder
from scipy.interpolate import interp1d
import astropy.units as u
import numpy as np

def light_curve(params, t=5.0*u.day, dt=0.5*u.day, threads=1):
    set_threads(threads)

    # Using R_phot = const for SN IIP
    t_0 = params['t_exp']
    R_phot = params['v_start']*t_0
    for i, t_i in enumerate(np.arange(t_0, t_0 + t, dt)):
        params['id'] = i
        params['t_exp'] = t_i
        params['v_start'] = R_phot / t_i
        run_tardis(params)

def photometry(log_scale, trans_x, trans_y, folder_path):
    scale = 10**log_scale
    param_names = ['t_exp', 'v_start']
    X, y, wav = parse_runs_folder(folder_path, param_names, sed_name='_integrated_sed.csv')
    y = interp1d(wav, y, bounds_error=False)(trans_x)*scale
    t = []
    L = []
    for run in X.itertuples():
        lum = np.sum(y * trans_y * abs(wav[1] - wav[0]))
        t.append(run.t_exp)
        L.append(lum)
    
    t = np.array(t)
    L = np.array(L)
    sorted = np.argsort(t)
    t = t[sorted]
    L = L[sorted]
    return t, L
