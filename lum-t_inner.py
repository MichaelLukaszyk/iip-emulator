# luminosity -> t_inner
import astropy.units as u
import json

from param_space import config, utilities, functions, classes
from param_space.run_tardis import run_tardis

def step_run(log_lsun):
    lum = utilities.from_loglsun(log_lsun)
    v_start = utilities.guess_v_start(lum)

    # Get min/max t_inner given luminosity
    def range_run(v):
        run_tardis(lum, v_start, v)
    t_inner = functions.find_range(
        range_run,
        16000 * u.K, # guess_t_inner(lum)
        **config.range_config["t_inner"]
    )
    if t_inner != None:
        min_entry = classes.RunEntry.new(log_lsun, v_start, t_inner["min"], 2, "min")
        max_entry = classes.RunEntry.new(log_lsun, v_start, t_inner["max"], 2, "max")
        
        with open(config.output_path, "a") as out_file:
            json.dump(min_entry.to_dict(), out_file)
            out_file.write("\n")
            json.dump(max_entry.to_dict(), out_file)
            out_file.write("\n")
    return t_inner

data = functions.step_through(
    step_run,
    **config.step_config["log_lsun"]
)