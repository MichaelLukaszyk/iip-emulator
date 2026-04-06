from emulator.grid_run.run_tardis import set_threads, run_tardis
from emulator.interpolator.util import parse_runs_folder
from scipy.interpolate import interp1d
from astropy.constants import c
from astropy.io import fits
import astropy.units as u
import numpy as np

def light_curve(params, t_list=None, t_min=None, t_max=None, dt=None, threads=1, config_path=None):
    set_threads(threads)

    # Using R_phot = const for SN IIP
    t_0 = params['t_exp'].to(u.day).value
    v_0 = params['v_phot'].to(u.km/u.s).value
    R_phot = v_0*t_0
    if t_min and t_max and dt and not t_list:
        t_list = np.arange(t_min, t_max, dt)
    for i, t_i in enumerate(t_list):
        if t_min and t_i < t_min:
            continue
        if t_max and t_i > t_max:
            continue

        params['id'] = i
        params['t_exp'] = t_i * u.day
        params['v_start'] = R_phot / t_i * u.km/u.s
        try:
            run_tardis(params, config_path=config_path)
        except Exception as e:
            print('Error:', e)

def get_sdss_flt():
    hdus = fits.open('/mnt/c/Users/mikel/Desktop/sdss_filter_curves.fits')
    flt = {}
    for i in np.arange(1, 6):
        hdu = hdus[i]
        data = hdu.data
        wave = data['wavelength']
        trans = data['respt']
        flt[hdu.name] = {'wave': wave, 'trans': trans}
    return flt

def ccd_ab_to_flux(m_AB, obs_wave, obs_flux_density, flt_wave, flt_trans):
    obs_flux_density = interp1d(obs_wave, obs_flux_density)(flt_wave)
    obs_flux = np.trapezoid(obs_flux_density * flt_trans * flt_wave, flt_wave) / np.trapezoid(flt_trans * flt_wave, flt_wave)

    # Convert to Jy
    lam_pivot = np.sqrt(
        np.trapezoid(flt_trans * flt_wave, flt_wave) /
        np.trapezoid(flt_trans / flt_wave, flt_wave)
    )
    lam_pivot *= u.AA
    obs_flux = (obs_flux * u.erg/u.s/u.AA/u.cm**2 * lam_pivot**2 / c).to(u.Jy)

    mag_flux = 3631 * 10**(-0.4*m_AB) * u.Jy
    return obs_flux, mag_flux

def flux_to_ab(wave, flux_density, flt_wave, flt_trans):
    flux = np.trapezoid(flux_density * flt_trans, flt_wave) / np.trapezoid(flt_trans, flt_wave)
    lam_pivot = np.sqrt(
        np.trapezoid(flt_trans * flt_wave, flt_wave) /
        np.trapezoid(flt_trans / flt_wave, flt_wave)
    )
    lam_pivot *= u.AA
    flux = (flux * u.erg/u.s/u.AA/u.cm**2 * lam_pivot**2 / c).to(u.Jy).value

    m_AB = -2.5 * np.log10(flux/3631)

def photometry(log_scale, flt_wave, flt_trans, folder_path, t_0, m_0):
    scale = 10**log_scale
    param_names = ['t_exp', 'v_start']
    X, y, wav = parse_runs_folder(folder_path, param_names, sed_name='_integrated_sed.csv')
    y = interp1d(wav, y)(flt_wave)/scale
    
    t = []
    f = []
    for i in range(len(X)):
        mod_flux_density = y[i]
        mod_flux = np.trapezoid(mod_flux_density * flt_trans, flt_wave) / np.trapezoid(flt_trans, flt_wave)
        t.append(X.iloc[i]['t_exp'])
        f.append(mod_flux)
    t = np.array(t)
    f = np.array(f)

    f_0 = f[np.argmin(np.abs(t - t_0))]
    m = m_0 - 2.5 * np.log10(f/f_0)
    sort = np.argsort(t)
    return t[sort], m[sort]
