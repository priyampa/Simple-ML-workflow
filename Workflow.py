#Imports
import argparse
import json
from functions import preprocessing, processing, post_processing,dicom_filter #Importing all functions for full pipeline (pre-processing,processing,post-processing and dicom filtering)

# Argument Parsing from Command line
parser1 = argparse.ArgumentParser()
parser1.add_argument("-i", "--input-dicom", help="path to input DICOM directory")
parser1.add_argument("-c", "--config", help="path to the configuration file")
parser1.add_argument("-o", "--output-dicom", help="path to output DICOM directory")
arguments = parser1.parse_args()

# Opening the JSON file which has the dictionary for configuration of the filtering
with open(arguments.config) as json_file:
    config_dict = json.load(json_file)

# Filtering the DICOM files with the config file
filtered_series_dict=dicom_filter(input_dir=arguments.input_dicom,config=config_dict)

# For each unique series seen in the files, pre-processing, processing and post-processing is done
for series in filtered_series_dict:
    output_json,sorted_pixel_array=preprocessing(filtered_series_dict[series])
    gaussian_blurred_array=processing(sorted_pixel_array)
    post_processing(gaussian_blurred_array,filtered_series_dict[series],output_dicom_dir=arguments.output_dicom)
