# Imports
import argparse #To parse the arguments
import numpy as np
import os
import json
from functions import DICOM_to_NUMPY # Importing Dicom to Numpy function from functions.py


path = os.getcwd() # Find current working directory

# Parsing arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input-dicom", help="path to input DICOM directory")
parser.add_argument("-n", "--output-npy", help="path to output numpy file",const="3Dnparray.npy",nargs="?")
parser.add_argument("-j", "--output-json", help="path to output json file",const="Sample.json",nargs="?")
args = parser.parse_args()

# Getting a list of filepaths for input dicoms
input_dicoms_filepaths=os.listdir(os.chdir(args.input_dicom))

# If the input dicom directory is given, then only execute the Dicom to Numpy function
if args.input_dicom!=None:
    output_dict,sorted_pixel_arrays=DICOM_to_NUMPY(input_dicoms_filepaths)

    os.chdir(path)
    with open(args.output_json, "w") as fp:
        json.dump(output_dict , fp) # Output JSON

    with open(args.output_npy, 'wb') as f:
        np.save(f, sorted_pixel_arrays) # Saving numpy array
