import astropy.units as u
import numpy as np
import yaml
import csv
import os

density = {
    "type": "power_law",
    "rho_0": "1.948e-14 g/cm^3",
    "v_0": "8000 km/s",
    "exponent": -10
}

current_dir = os.path.dirname(os.path.abspath(__file__))
default_path = os.path.join(current_dir, "tardis_data/model.csvy")

def make_abundances(X, Z):
    # Solar metallicity values 'vSZ16' from Vagnozzi (2019)
    metals = {
        'C': 0.003902,
        'N': 0.000951,
        'O': 0.007688,
        'Ne': 0.000905,
        'Mg': 0.001252,
        'Si': 0.001350,
        'S': 0.000847,
        'Fe': 0.002181
    }
    Y = 1 - X - Z
    s = sum(metals.values())
    for i in metals:
        metals[i] *= Z / s
    abundances = {'H': X, 'He': Y, **metals}
    return abundances

default_abundances = make_abundances(0.7, 0.02)

def make_csvy(v_start, v_stop, shells, csvy_path=default_path, abundances=default_abundances):
    with open(csvy_path, "w") as file:
        units = v_start.unit
        start = v_start.value
        stop = v_stop.to(units).value

        # Write csv metadata
        metadata = {
            "tardis_model_config_version": "v1.0",
            "model_density_time_0": "16.0 day",
            "model_isotope_time_0": "100 s",
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
        for key in abundances.keys():
            metadata["datatype"]["fields"].append({
                "name": key
            })
        metadata["datatype"]["fields"][0]["unit"] = str(units)
        file.write("---\n")
        yaml.dump(metadata, file)
        file.write("---\n")

        # Calculate power law densities
        rho_0 = u.Quantity(density["rho_0"])
        v_0 = u.Quantity(density["v_0"])
        log_start = 2.5
        velocities = (np.logspace(log_start, np.log10(stop-start+10**log_start), num=shells+1) + start - 10**log_start)*units
        densities = rho_0 * (velocities / v_0)**density["exponent"]

        # Write csv shell content
        fields = ["velocity", "density"] + list(abundances.keys())
        shells = [[velocities[i].value, densities[i].to(u.g / u.cm**3).value] + list(abundances.values()) for i in range(1 + shells)]
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(shells)