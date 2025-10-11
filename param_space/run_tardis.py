from tardis.io.configuration.config_reader import Configuration
from tardis.simulation import Simulation
from tardis.io.atom_data.base import AtomData
from param_space.make_csvy import make_csvy
from param_space.functions import write_df
from param_space import utilities
import astropy.units as u
import pandas as pd
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

def run_tardis(params, run_index=0):
    # Setup CSVY, then load data
    v_start = params['v_start'] or (6200 * u.km/u.s)
    make_csvy(
        v_start,
        v_stop = v_start * 3,
        shells = 10
    )
    current_dir = os.path.dirname(os.path.abspath(__file__))
    atomic = AtomData.from_hdf(os.path.join(current_dir, 'tardis_data/atom_data.h5'))
    config = Configuration.from_yaml(os.path.join(current_dir, 'tardis_data/base_config.yml'))

    # Update configuration with params
    for name, value in params.items():
        if name == 'lum':
            config.supernova.luminosity_requested = value
        elif name == 'log_lsun':
            config.supernova.luminosity_requested = utilities.from_loglsun(value)
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
        log_level='CRITICAL'
    )
    sim.run_convergence()
    sim.run_final()

    # Run was successful: assign ID, log SED data
    id = str(run_index)
    params['id'] = id
    wavelength = sim.spectrum_solver.spectrum_virtual_packets.wavelength
    L_density = sim.spectrum_solver.spectrum_virtual_packets.luminosity_density_lambda
    df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    write_df(df, id + '_sed')