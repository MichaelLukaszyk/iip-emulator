# luminosity -> t_inner
import astropy.units as u
import json

from param_space import config, utilities, functions, classes
from param_space.run_tardis import run_tardis

log_lsun = 9.5
lum = utilities.from_loglsun(log_lsun)
v_start = utilities.guess_v_start(lum)

def range_run(v):
    run_tardis(lum, v_start, v)
t_inner = functions.find_range(
    range_run,
    16000 * u.K,
    **config.range_config["t_inner"]
)
if t_inner != None:
    min_entry = classes.RunEntry.new(log_lsun, v_start, t_inner["min"], 2, "min")
    max_entry = classes.RunEntry.new(log_lsun, v_start, t_inner["max"], 2, "max")
    print("min:", min_entry)
    print("max:", max_entry)