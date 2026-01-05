from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import astropy.units as u
import pandas as pd
import numpy as np
import os

def read_grid_runs(folder_path, param_names):
    params_df = pd.read_json(os.path.join(folder_path, 'parameters.log'), lines=True)
    params_df = params_df[params_df['converged'] == True]
    wav = None
    seds = []
    for run in params_df.itertuples():
        sed_df = pd.read_csv(os.path.join(folder_path, str(run.id) + '_integrated_sed.csv'))
        seds.append(sed_df['L_density'].values)
        if wav is None:
            wav = sed_df['wavelength'].values

    def convert(v):
        return u.Quantity(v).value
    X = params_df[param_names].map(convert)
    y = np.array(seds)
    return X, y, wav

def evaluate_predictions(y_test, y_pred, x_axis, title):
    with np.errstate(all='ignore'):
        # fe = np.abs(np.log10(y_pred + 1) - np.log10(y_test + 1)) / np.log10(y_test + 1)
        fe = np.abs((y_pred - y_test) / y_test)
        fe[np.isinf(fe)] = np.nan
        mfe = np.nanmean(fe, axis=1)

    # Filter out predictions that have an invalid mfe
    mask = np.isfinite(mfe)
    fe = fe[mask]
    mfe = mfe[mask]
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
        plt.plot(x_axis, preds[index], c=color, label=type + ' mfe: ' + f'{mfe[index]:.1e}')
        plt.plot(x_axis, tests[index], c=color, ls=':')
    plt.title(title)
    plt.legend()

    # Histogram
    plt.subplot(122)
    mask = mfe <= np.percentile(mfe, 95)
    plt.hist(mfe[mask], 100)
    plt.title(title)
    plt.xlabel('mean fractional error')

    print('mean mfe: ' + f'{np.mean(mfe):.1e}')

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