from tardis.io.configuration.config_reader import Configuration
from tardis.simulation import Simulation
from tardis.io.atom_data.base import AtomData
from param_space.make_csvy import make_csvy
from param_space.functions import write_df
from param_space import utilities
import pandas as pd
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
run_indices = {}

def run_tardis(params, output_name):
    # Setup CSVY, then load data
    make_csvy(
        params["v_start"],
        v_stop = params["v_start"] * 3,
        shells = 10
    )
    current_dir = os.path.dirname(os.path.abspath(__file__))
    atomic = AtomData.from_hdf(os.path.join(current_dir, "tardis_data/atom_data.h5"))
    config = Configuration.from_yaml(os.path.join(current_dir, "tardis_data/base_config.yml"))

    # Update configuration with params
    for name, value in params.items():
        if name == "lum":
            config.supernova.luminosity_requested = value
        elif name == "log_lsun":
            config.supernova.luminosity_requested = utilities.from_loglsun(value)
        elif name == "t_exp":
            config.supernova.time_explosion = value
        elif name == "t_inner":
            config.plasma.initial_t_inner = value

    # Run simulation
    sim = Simulation.from_config(
        config,
        atom_data = atomic,
        log_level="CRITICAL"
    )
    sim.run_convergence()
    sim.run_final()

    # Run was successful: assign ID, log SED data
    global run_indices
    if not output_name in run_indices:
        run_indices[output_name] = 1
    index = run_indices[output_name]
    run_indices[output_name] += 1
    id = output_name + '_' + str(index)
    params['id'] = id
    wavelength = sim.spectrum_solver.spectrum_virtual_packets.wavelength
    L_density = sim.spectrum_solver.spectrum_virtual_packets.luminosity_density_lambda
    df = pd.DataFrame({'wavelength': wavelength, 'L_density': L_density})
    write_df(df, id + '_sed')