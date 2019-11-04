"""
Linearly interpolates absorbance between each wavenumber,
and outputs a constant data point spacing of 1.929 cm^-1 for a wavenumber range of 450 - 4000 cm^-1.

Author: Rasmus Vest Nielsen
"""

from scipy.interpolate import interp1d
import pandas as pd
import numpy as np
import os
import glob

# Load spectra data.
spectra_file_names = glob.glob("spectra_csv/*.csv")

spectra_counter = 0
df_list = [] # List containing all spectra.
for spectra_file_name in spectra_file_names:

    df_spectra = pd.read_csv(spectra_file_name,
            usecols = [1, 2])
    
    # Due to inaccurate estimation of x-axis,
    # the start and end wavenumber is forced to
    # match the OMNIC library specifications.
    # Typically, we have an error of 1 to 2
    # cm^-1 dependent on how precise the 
    # operator of graphffer.py set the axis start
    # and end point.
    df_spectra["wavenumbers"].iloc[0] = 450
    df_spectra["wavenumbers"].iloc[-1] = 4000

    #print(df_spectra)

    wavenumbers = df_spectra["wavenumbers"]
    absorbance = df_spectra["absorbance"]

    # Perform linear interpolation between each
    # wavenumber.
    f = interp1d(wavenumbers, absorbance)

    # Generate new interval.
    constant_rate_wavenumbers = np.arange(450, 
            4001, 1.929)
    #constant_rate_wavenumbers[-1] = 4000
    #print(constant_rate_wavenumbers)

    constant_rate_absorbance = f(
            constant_rate_wavenumbers)
    #print(constant_rate_absorbance)

    out_dir = "constant_rate_spectra"
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    # Get index of spectra.
    spectra_idx = spectra_file_name.split(
            "\\")[1].split(".")[0]

    d = {"wavenumber": constant_rate_wavenumbers,
         spectra_idx + "_absorbance": 
         constant_rate_absorbance}

    df_tmp = pd.DataFrame(data = d)
    df_tmp = df_tmp.set_index("wavenumber")
    df_list.append(df_tmp)

# Concatenate each of spectra.
df = pd.concat(df_list, axis = 1)
df.to_csv(out_dir + "/spectra.csv")
