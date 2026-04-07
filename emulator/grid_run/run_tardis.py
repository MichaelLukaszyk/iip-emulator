from tardis.io.configuration.config_reader import Configuration
from tardis.simulation import Simulation
from emulator.grid_run.make_csvy import make_csvy, make_abundances
from emulator.grid_run.output import write_data, write_df
from scipy.interpolate import interp1d
import astropy.constants as const
import astropy.units as u
import pandas as pd
import numpy as np
import os

def set_threads(threads):
    os.environ['OMP_NUM_THREADS'] = str(threads)
    os.environ['MKL_NUM_THREADS'] = str(threads)
    os.environ['NUMEXPR_NUM_THREADS'] = str(threads)

def standard_csvy(params, config_path=None):
    v_start = 6200 * u.km/u.s
    abundances = None
    n = None
    if 'v_start' in params:
        v_start = params['v_start']
    if 'n' in params:
        n = params['n']
    if 'X' in params and 'Z' in params:
        abundances = make_abundances(params['X'], params['Z'])
        
    make_csvy(
        v_start,
        v_stop=v_start*3,
        shells=40,
        n=n,
        config_path=config_path,
        abundances=abundances
    )

def build_config(params, config_path=None):
    if not config_path:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'tardis_data/base_config.yml')
    config = Configuration.from_yaml(config_path)
    
    for name, value in params.items():
        if name == 'lum':
            config.supernova.luminosity_requested = value
        elif name == 'log_lsun':
            config.supernova.luminosity_requested = 10**value * const.L_sun
        elif name == 't_exp':
            config.supernova.time_explosion = value
        elif name == 't_inner':
            config.plasma.initial_t_inner = value
        elif name == 'seed':
            config.montecarlo.seed = value
        elif name == 'packets':
            config.montecarlo.no_of_packets = value
        elif name == 'last_packets':
            config.montecarlo.last_no_of_packets = value
        elif name == 'virtual_packets':
            config.montecarlo.no_of_virtual_packets = value
    return config

def thomson_tau(sim):
    n_e = sim.plasma.electron_densities
    sigma_T = const.sigma_T.cgs.value
    kappa = n_e * sigma_T
    v = ((sim.simulation_state.v_outer + sim.simulation_state.v_inner) / 2).cgs.value
    dr = (sim.simulation_state.r_outer - sim.simulation_state.r_inner).cgs.value
    tau = np.flip(np.cumsum(np.flip(kappa * dr)))
    return v, tau

def get_tau(sim, t_exp, plot=False, bin_size=10):
    # Credit: Jack O'Brien
    index = sim.plasma.atomic_data.lines.nu.index
    taus = sim.plasma.tau_sobolevs.loc[index]
    freqs = sim.plasma.atomic_data.lines.nu.values
    order = np.argsort(freqs)
    freqs = freqs[order]
    taus = sim.plasma.tau_sobolevs.values[order]

    extra = bin_size - len(freqs) % bin_size
    extra_freqs = np.arange(extra + 1 ) + 1
    extra_taus = np.zeros((extra + 1, taus.shape[1]))
    freqs = np.hstack((extra_freqs, freqs))
    taus = np.vstack((extra_taus, taus))

    bins_low = freqs[:-bin_size:bin_size]
    bins_high = freqs[bin_size::bin_size]
    delta_nu = bins_high - bins_low
    n_bins = len(delta_nu)

    taus = taus[1:n_bins*bin_size+1]
    freqs = freqs[1:n_bins*bin_size+1]
    t_rad = sim.plasma.t_rad
    dr = (sim.simulation_state.r_outer - sim.simulation_state.r_inner).cgs.value

    # Thomson
    sigma_T = const.sigma_T.cgs.value
    n_e = sim.plasma.electron_densities.values
    kappa_thom = (n_e * sigma_T)
    tau_thomson = np.flip(np.cumsum(np.flip(kappa_thom * dr)))

    h = const.h.cgs.value
    c = const.c.cgs.value
    kb = const.k_B.cgs.value
    def B(nu, T):
        return 2*h*nu**3/c**2/(np.exp(h*nu/(kb*T))-1)
    def U(nu, T):
        return B(nu, T)**2 * (c/nu)**2 * (2*kb*T**2)**-1

    # Expansion
    ct = ((t_exp*u.day*const.c).cgs.value)
    kappa_exp = (bins_low / delta_nu).reshape(-1, 1) / ct * (1 - np.exp(-taus.reshape(n_bins, bin_size, -1))).sum(axis=1)
    Bdnu = B(bins_low.reshape(-1, 1), t_rad.reshape(1, -1))*delta_nu.reshape(-1, 1)
    tau_expansion = np.flip(np.cumsum(np.flip((Bdnu * kappa_exp).sum(axis=0) / (Bdnu.sum(axis=0)) * dr)))

    # Planck
    kappa_planck = (kappa_thom + (Bdnu * kappa_exp).sum(axis=0) / (Bdnu.sum(axis=0)))
    tau_planck = np.flip(np.cumsum(np.flip(kappa_planck * dr)))

    # Rosseland
    udnu = U(bins_low.reshape(-1, 1), t_rad.reshape(1, -1))*delta_nu.reshape(-1, 1)
    kappa_tot = kappa_thom + kappa_exp
    kappa_rosseland = ((udnu / kappa_tot).sum(axis=0) / (udnu.sum(axis=0)))**-1
    tau_rosseland = np.flip(np.cumsum(np.flip(kappa_rosseland * dr)))

    v = ((sim.simulation_state.v_outer + sim.simulation_state.v_inner) / 2).to(u.km/u.s).value
    if plot:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(v, tau_planck, label='Planck')
        plt.plot(v, tau_rosseland, label='Rossland')
        plt.plot(v, tau_thomson, label='Thomson')
        plt.plot(v, tau_expansion, label='Expansion')
        plt.xlabel('v (km/s)')
        plt.ylabel('tau')
        plt.yscale('log')
        plt.legend()
    kappa_planck
    return v, tau_thomson, tau_expansion, tau_planck, tau_rosseland

def get_phot(sim, v, tau, tau_phot=2.0/3):
    T = sim.plasma.t_rad
    v_phot = interp1d(tau, v)(tau_phot)
    T_phot = interp1d(tau, T)(tau_phot)
    return v_phot, T_phot

def log_sim(params, sim):
    # Any modifications to params will be written to parameters.log by write_data
    id = params['id']
    params['converged'] = sim.converged
    params['iterations'] = str(sim.iterations_executed) + '/' + str(sim.iterations)
    v, tau_thomson, tau_expansion, tau_planck, tau_rosseland = get_tau(sim, params['t_exp'].value)
    v_phot, T_phot = get_phot(sim, v, tau_rosseland)
    params['v_phot'] = v_phot
    params['T_phot'] = T_phot
    params['T_inner'] = sim.plasma.t_rad[0]

    # wavelength = sim.spectrum_solver.spectrum_virtual_packets.wavelength
    # L_density = sim.spectrum_solver.spectrum_virtual_packets.luminosity_density_lambda
    # df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    # write_df(df, str(id) + '_virtual_sed')

    wavelength = sim.spectrum_solver.spectrum_integrated.wavelength
    L_density = sim.spectrum_solver.spectrum_integrated.luminosity_density_lambda
    df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    write_df(df, str(id) + '_integrated_sed')

    write_data(params)

def run_tardis(params, config_path=None):
    standard_csvy(params, config_path=config_path)
    config = build_config(params, config_path=config_path)
    sim = Simulation.from_config(
        config,
        virtual_packet_logging=False,
        show_convergence_plots=False,
        export_convergence_plots=False,
        log_level='CRITICAL',
    )
    sim.run_convergence()
    sim.run_final()
    log_sim(params, sim)