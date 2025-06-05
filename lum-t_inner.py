# luminosity -> t_inner
import astropy.units as u
import json

import ParamSpace.Config as Config
import ParamSpace.Utilities as Util
import ParamSpace.RunFuncs as Funcs
import ParamSpace.Classes as Classes

def step_run(log_lsun):
    lum = Util.from_loglsun(log_lsun)
    v_start = Util.guess_v_start(lum)

    # Get min/max t_inner given luminosity
    def range_run(v):
        Funcs.run(lum, v_start, v)
    t_inner = Funcs.find_range(
        range_run,
        16000 * u.K, # guess_t_inner(lum)
        **Config.range_config["t_inner"]
    )
    if t_inner != None:
        min_entry = Classes.RunEntry.new(log_lsun, v_start, t_inner["min"], 2, "min")
        max_entry = Classes.RunEntry.new(log_lsun, v_start, t_inner["max"], 2, "max")
        
        with open(Config.output_path, "a") as out_file:
            json.dump(min_entry.to_dict(), out_file)
            out_file.write("\n")
            json.dump(max_entry.to_dict(), out_file)
            out_file.write("\n")
    return t_inner

data = Funcs.step_through(
    step_run,
    **Config.step_config["log_lsun"]
)