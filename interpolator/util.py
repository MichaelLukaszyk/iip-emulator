from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
import numpy as np

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