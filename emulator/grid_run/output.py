import astropy.units as u
import json
import os

output_dir = None
folder_dir = None

def get_output_dir():
    return output_dir

def get_folder_dir():
    return folder_dir

def set_output_dir(new_output_dir):
    global output_dir
    output_dir = new_output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def set_folder_name(output_name):
    global folder_dir
    folder_dir = os.path.join(output_dir, output_name)
    if not os.path.exists(folder_dir):
        os.makedirs(folder_dir)

def convert_quantities(data):
    if type(data) == dict:
        for key, value in data.items():
            if type(value) == u.Quantity:
                data[key] = str(value)
            elif type(value) == dict:
                convert_quantities(value)
    return data

def write_data(data):
    file_path = os.path.join(folder_dir, 'parameters.log')
    with open(file_path, 'a') as file:
        json.dump(convert_quantities(data), file)
        file.write('\n')

def write_df(df, name):
    file_path = os.path.join(folder_dir, name + '.csv')
    df.to_csv(file_path, index=False)