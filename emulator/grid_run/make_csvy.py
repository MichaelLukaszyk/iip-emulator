from emulator.interpolator import util
import astropy.units as u
import numpy as np
import yaml
import csv
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
default_path = os.path.join(current_dir, 'tardis_data/model.csvy')

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

def make_csvy(shells, t_exp, X, n=10, config_path=None, abundances=default_abundances, v_start=None):
    # CSVY model must be in same directory as configuration
    if config_path:
        csvy_path = os.path.join(os.path.dirname(config_path), 'model.csvy')
    else:
        csvy_path = default_path
    with open(csvy_path, 'w') as file:
        # Write CSVY metadata
        metadata = {
            'tardis_model_config_version': 'v1.0',
            'model_density_time_0': '16.0 day',
            'model_isotope_time_0': '100 s',
            'name': 'model.csvy',

            'datatype': {
                'fields': [
                    {
                        'name': 'velocity',
                        'unit': 'km/s',
                    },
                    {
                        'name': 'density',
                        'unit': 'g/cm^3'
                    }
                ]
            }
        }
        for key in abundances.keys():
            metadata['datatype']['fields'].append({
                'name': key
            })
        file.write('---\n')
        yaml.dump(metadata, file)
        file.write('---\n')

        # Calculate power law densities
        if v_start:
            v_phot = v_start
        else:
            v_phot = util.calc_v_phot(t_exp=t_exp, X=X, n=n)
        # v_outer = 3 * v_phot
        v_outer = util.calc_v_outer(v_phot=v_phot, n=n)
        rho_0 = 1.948e-14
        v_0 = 8000.0
        log_start = 3.0
        velocities = np.logspace(log_start, np.log10(v_outer-v_phot+10**log_start), num=shells+1) + v_phot - 10**log_start
        densities = rho_0 * (velocities / v_0)**(-n)

        # Write CSVY shell content
        fields = ['velocity', 'density'] + list(abundances.keys())
        shells = [[velocities[i], densities[i]] + list(abundances.values()) for i in range(1 + shells)]
        writer = csv.writer(file)
        writer.writerow(fields)
        writer.writerows(shells)