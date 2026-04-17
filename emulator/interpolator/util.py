from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import astropy.units as u
import pandas as pd
import numpy as np
import os
from astropy.constants import L_sun, m_p, sigma_T, sigma_sb

def remove_bad_indices(X, y, bad_indices):
    mask = ~np.isin(np.arange(len(X)), bad_indices)
    return X[mask], y[mask]

def distance(scale):
    # Spectral flux in erg/s/ang/cm^2, model luminosity in erg/s/ang
    # F = (1/k)L, k = 4*pi*d^2
    return (np.sqrt(scale/4/np.pi) * u.cm).to(u.Mpc)

def blackbody_L(t_exp, T, v):
    r = v*t_exp
    L = 4*np.pi*r**2 * sigma_sb * T**4
    return L.to(u.erg/u.s)

def to_loglsun(lum):
    return np.log10((lum/L_sun).to(u.dimensionless_unscaled))

def to_lum(log_lsun):
    return (10**log_lsun*L_sun).to(u.erg/u.s)

def calc_v_outer(v_phot, n):
    return v_phot*(0.01)**(-1/n)

def calc_v_phot(t_exp, X, n):
    rho_0 = 1.948e-14 * u.g/u.cm**3
    t_0 = 10.0 * u.day
    v_0 = 8000.0 * u.km/u.s
    t_exp *= u.day
    tau = 2.0/3
    numer = sigma_T * t_exp * rho_0 * v_0 * X * (t_0 / t_exp)**3
    denom = tau * m_p * (n-1)
    v_phot = v_0 * (numer/denom).to(u.dimensionless_unscaled)**(1/(n-1))
    return v_phot.to(u.km/u.s).value

def calc_v_phot_simplified(t_exp, X, n, rho_0=1.948e-14):
    # This assumes v_0 = v, and t_0 = t
    t_exp *= u.day
    rho_0 *= u.g/u.cm**3
    tau = 2.0/3
    v_phot = tau*m_p*(n-1)/(sigma_T*t_exp*rho_0*X)
    return v_phot.to(u.km/u.s).value

def calc_model_mass(t_exp, v_phot, v_outer, n, rho_0=1.948e-14):
    t_exp *= u.day
    v_phot *= u.km/u.s
    v_outer *= u.km/u.s
    rho_0 *= u.g/u.cm**3
    M = 4*np.pi*rho_0 * t_exp**3 * v_phot**n / (n-3) * (v_phot**(3-n) - v_outer**(3-n))
    E = 2*np.pi*rho_0 * t_exp**3 * v_phot**n / (n-5) * (v_phot**(5-n) - v_outer**(5-n))
    return M.to(u.kg), E.to(u.erg)

def initial_t_inner(L, t_exp, v_start):
    R_inner = v_start * t_exp
    A = 4 * np.pi * R_inner**2 * sigma_sb
    return ((L / A)**0.25).to(u.K)

def parse_runs_folder(folder_path, param_names, sed_name='_integrated_sed.csv'):
    params_df = pd.read_json(os.path.join(folder_path, 'parameters.log'), lines=True)
    params_df = params_df[params_df['converged'] == True]
    wav = None
    seds = []
    for run in params_df.itertuples():
        sed_df = pd.read_csv(os.path.join(folder_path, str(run.id) + sed_name))
        seds.append(sed_df['L_density'].values)
        if wav is None:
            wav = sed_df['wavelength'].values

    def convert(v):
        return u.Quantity(v).value
    X = params_df[param_names].map(convert)
    y = np.array(seds)
    return X, y, wav

def save_runs(folder_path, param_names, file_name, sed_name='_integrated_sed.csv'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(current_dir, '../user_data/saved_runs/')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    X, y, wav_mod = parse_runs_folder(folder_path, param_names, sed_name)
    np.savez(
        save_dir + file_name + '.npz',
        param_names=param_names,
        X=X,
        y=y,
        wav=wav_mod
    )

def read_runs(file_name):
    """
    Parameters:
        file_name (string): The name used when saving the original file, no file type included.
    
    Returns:
        param_names, X, y, wav_mod
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    save_path = os.path.join(current_dir, '../user_data/saved_runs/' + file_name + '.npz')
    if os.path.exists(save_path):
        data = np.load(save_path)
        param_names, X, y, wav_mod = data['param_names'], data['X'], data['y'], data['wav']
        return param_names, X, y, wav_mod

def evaluate_predictions(y_test, y_pred, x_axis, title):
    with np.errstate(all='ignore'):
        fe = np.abs((y_pred - y_test) / y_test)
        fe[np.isinf(fe)] = np.nan
        actual_mfe = np.nanmean(fe, axis=1)

    # Filter out predictions that have an invalid mfe
    mask = np.isfinite(actual_mfe) & (actual_mfe <= np.percentile(actual_mfe, 95))
    fe = fe[mask]
    mfe = actual_mfe[mask]
    tests = y_test[mask]
    preds = y_pred[mask]

    # Sort by mfe
    total = len(mfe)
    sorted_indices = np.argsort(mfe)
    min_i = sorted_indices[0]
    med_i = sorted_indices[total // 2]
    max_i = sorted_indices[total - 1]

    # Plot best, median, and worst predictions
    plt.figure(figsize=(11, 4))
    plt.subplot(121)
    for index, color, type in [(min_i, 'green', 'best'), (med_i, 'orange', 'median'), (max_i, 'red', 'worst')]:
        plt.plot(x_axis, preds[index] / tests[index].max(), c=color, label=type + ' mfe: ' + f'{mfe[index]:.1e}')
        plt.plot(x_axis, tests[index] / tests[index].max(), c=color, ls=':')
    plt.xlabel(r'Wavelength ($\AA$)')
    plt.ylabel('Normalized flux')
    plt.legend()

    # Histogram
    plt.subplot(122)
    plt.hist(mfe, 100)
    plt.xlabel('Mean fractional error')
    plt.ylabel('Count')
    
    plt.suptitle(title)
    return actual_mfe

def outline_mask_region(x, mask):
    trues = np.where(mask)[0]
    plt.axvline(x[trues[0]], ls='--', c='black')
    plt.axvline(x[trues[-1]], ls='--', c='black')

def label_common_features():
    lines = {
        "Hα": 6562.8,
        "Hβ": 4861.3,
        "Hγ": 4340.5,
        "He I": 5875.6,
        "Na I D": 5892,
        "Ca II (8498)": 8498,
        "Ca II (8542)": 8542,
        "Ca II (8662)": 8662,
        "Fe II (5169)": 5169,
    }
    label_heights = {
        "Na I D": 0.5,
        "Ca II (8498)": 0.7,
        "Ca II (8542)": 0.4,
        "Ca II (8662)": 0.1,
    }
    i = 0
    ax = plt.gca()
    xmin, xmax = plt.xlim()
    for name, value in lines.items():
        if value > xmin and value < xmax:
            plt.axvline(value, color='red', linestyle='--', alpha=0.5)
            height = name in label_heights and label_heights[name] or 0.1
            plt.text(value + 15, height, name, rotation=90, fontsize=11, transform=ax.get_xaxis_transform())

def find_dx(x1, y1, x2, y2, dx_bounds, subtract_mean=False):
    # Shift x2 to minimize diff
    def shift_x(dx):
        y2_n = interp1d(x2 + dx, y2, bounds_error=False, fill_value=np.nan)(x1)
        mask = ~(np.isnan(y1) | np.isnan(y2_n))
        y1_n = y1[mask]
        y2_n = y2_n[mask]
        if y1_n.size == 0 or y2_n.size == 0:
            return np.inf
        
        # Subtract mean if shape is more important than magnitude
        if subtract_mean:
            y1_n -= np.mean(y1_n)
            y2_n -= np.mean(y2_n)

        # Number of points y2_n can have if fully overlapping with x1
        n1 = len(x1)
        n2 = (np.max(x2) - np.min(x2)) / (x1[1] - x1[0])
        n_max = min(n1, n2)

        # At least half the data points must overlap
        if len(y2_n) < n_max / 2:
            return np.inf
        else:
            return np.sum((y2_n - y1_n)**2) / n1
    result = minimize_scalar(shift_x, bounds=dx_bounds, method='bounded')
    dx = result.x
    mse = result.fun
    return dx, mse