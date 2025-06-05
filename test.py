# luminosity -> t_inner
import astropy.units as u
import json

import ParamSpace.Config as Config
import ParamSpace.Utilities as Util
import ParamSpace.RunFuncs as Funcs
import ParamSpace.Classes as Classes

log_lsun = 9.5
lum = Util.from_loglsun(log_lsun)
v_start = Util.guess_v_start(lum)

def range_run(v):
        Funcs.run(lum, v_start, v)
t_inner = Funcs.find_range(
    range_run,
    16000 * u.K,
    **Config.range_config["t_inner"]
)
if t_inner != None:
    min_entry = Classes.RunEntry.new(log_lsun, v_start, t_inner["min"], 2, "min")
    max_entry = Classes.RunEntry.new(log_lsun, v_start, t_inner["max"], 2, "max")
    print("min:", min_entry)
    print("max:", max_entry)