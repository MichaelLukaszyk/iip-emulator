from tardis.io.configuration.config_reader import Configuration
from tardis.simulation import Simulation
from tardis.io.atom_data.base import AtomData
from grid_run.make_csvy import make_csvy, make_abundances
from grid_run.functions import write_data, write_df
import astropy.constants as c
import astropy.units as u
import pandas as pd
import os

os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

def run_tardis(params):
    id = params['id']

    # Setup CSVY, then load data
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
        shells=10,
        n=n,
        abundances=abundances
    )
    current_dir = os.path.dirname(os.path.abspath(__file__))
    atomic = AtomData.from_hdf(os.path.join(current_dir, 'tardis_data/atom_data.h5'))
    config = Configuration.from_yaml(os.path.join(current_dir, 'tardis_data/base_config.yml'))

    # Update configuration with params
    for name, value in params.items():
        if name == 'lum':
            config.supernova.luminosity_requested = value
        elif name == 'log_lsun':
            config.supernova.luminosity_requested = 10**value * c.L_sun
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

    # Run simulation
    sim = Simulation.from_config(
        config,
        atom_data = atomic,
        virtual_packet_logging=False,
        show_convergence_plots=False,
        export_convergence_plots=False,
        log_level='CRITICAL',
    )
    sim.run_convergence()
    sim.run_final()

    # Run was successful: modify params, log SED data
    # Any modifications to params will be written to parameters.log by write_data
    params['converged'] = sim.converged
    params['iterations'] = str(sim.iterations_executed) + '/' + str(sim.iterations)

    wavelength = sim.spectrum_solver.spectrum_virtual_packets.wavelength
    L_density = sim.spectrum_solver.spectrum_virtual_packets.luminosity_density_lambda
    df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    write_df(df, str(id) + '_virtual_sed')

    wavelength = sim.spectrum_solver.spectrum_integrated.wavelength
    L_density = sim.spectrum_solver.spectrum_integrated.luminosity_density_lambda
    df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    write_df(df, str(id) + '_integrated_sed')

    write_data(params)