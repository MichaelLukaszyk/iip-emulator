import astropy.units as u
import numpy as np
import yaml
import csv
import os

metadata = {
    "tardis_model_config_version": "v1.0",
    #"model_density_time_0": "16 day",
    "model_isotope_time_0": "0 day",
    "name": "model.csvy",

    "datatype": {
        "fields": [
            {
                "name": "velocity",
                "unit": "km/s",
            },
            {
                "name": "density",
                "unit": "g/cm^3"
            }
        ]
    }
}

density = {
    "type": "power_law",
    "time_0": "16.0 day",
    "rho_0": "1.948e-14 g/cm^3",
    "v_0": "8000 km/s",
    "exponent": -10
}

abundances = {
    "H": 0.7,
    "He": 0.28,
    "C": 1.44e-4,
    "N": 6.7e-3,
    "O": 1.13e-4,
    "Ni56": 1.3043e-2 
}

for key in abundances.keys():
    metadata["datatype"]["fields"].append({
        "name": key
    })

current_dir = os.path.dirname(os.path.abspath(__file__))
csvy_path = os.path.join(current_dir, "tardis_data/model.csvy")
fields = ["velocity", "density"] + list(abundances.keys())

def make_csvy(v_start, v_stop, t_exp, shells):
    units = v_start.unit
    start = v_start.value
    stop = v_stop.to(units).value

    with open(csvy_path, "w") as file:
        metadata["datatype"]["fields"][0]["unit"] = str(units)
        metadata["model_isotope_time_0"] = str(t_exp)
        file.write("---\n")
        yaml.dump(metadata, file)
        file.write("---\n")

        rho_0 = u.Quantity(density["rho_0"])
        v_0 = u.Quantity(density["v_0"])
        t_0 = u.Quantity(density["time_0"])

        velocities = np.logspace(np.log10(start), np.log10(stop), num = shells + 1) * units
        densities = rho_0 * (velocities / v_0)**density["exponent"] * (t_0 / t_exp)**3

        r = (velocities * t_exp).to(u.cm)
        print("r:", r[0])
        print("density:", densities[0])

        shells = [[velocities[i].value, densities[i].to(u.g / u.cm**3).value] + list(abundances.values()) for i in range(1 + shells)]

        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(shells)