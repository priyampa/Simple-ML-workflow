# Imports
import argparse
import pydicom
import numpy as np
import os
import json
from functions import NUMPY_to_DICOM # Numpy to dicom function from functions

# Argument Parser
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--input-npy", help="path to input numpy file")
parser.add_argument("-d", "--input-dicom", help="path to template DICOM directory")
parser.add_argument("-o", "--output-dicom", help="path to output DICOM directory")
args = parser.parse_args()
input_array=np.load(args.input_npy)
# Getting a list of filepaths for input dicoms

input_dicoms_filepaths=os.listdir(os.chdir(args.input_dicom))

# If the input dicom directory and input numpy file is given, then only execute the Numpy to Dicom function
if (args.input_npy!=None) and (args.input_dicom!=None):
    NUMPY_to_DICOM(input_array,input_dicoms_filepaths,args.output_dicom)

        

