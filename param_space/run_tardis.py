from tardis.io.configuration.config_reader import Configuration
from tardis.simulation import Simulation
from tardis.io.atom_data.base import AtomData
from param_space import utilities
import os

os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"
os.environ["NUMEXPR_NUM_THREADS"] = "4"

def run_tardis(lum, v_start, t_inner):
    print("Attempting:", utilities.to_loglsun(lum), v_start, t_inner)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    atomic = AtomData.from_hdf(os.path.join(current_dir, "tardis_data/atom_data.h5"))
    config = Configuration.from_yaml(os.path.join(current_dir, "tardis_data/base_config.yml"))
    
    config.supernova.luminosity_requested = lum
    config.model.structure.velocity.start = v_start
    config.model.structure.velocity.stop = v_start * 3
    config.plasma.initial_t_inner = t_inner

    sim = Simulation.from_config(
        config,
        atom_data = atomic,
        log_level="CRITICAL"
    )
    sim.run_convergence()
    sim.run_final()