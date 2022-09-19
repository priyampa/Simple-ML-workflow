# README

This repository is an end-to-end pipeline for DICOM images.
The DICOM images are:
1)Pre-Processed: The images are given in the form of slices and are stitched together and normalized to [0,1]. This results in a 3D volume of numpy array. 
2) Processed: After creation of a 3D numpy array, we can apply various filters on it. For this particular repository, I have applied a 3D Gaussian blurring filter to blur the voxels in all the 3 dimensions.
3) Post- Processed: After Processing, the DICOM images are scaled back to their original size and then they are also saved in new DICOM files.

## Dependencies
1. Python 3.7+ (https://www.python.org/downloads/) Download suitable version for your machine
2. numpy- (pip install numpy)
3. pydicom- (pip install pydicom)

## functions.py
This script is the brain of the repository and has all the functions required to run this program:
Function List:
1. dicom_filter - Filters the DICOM series from the input directory based on a configuration
2. DICOM_to_NUMPY - Converts the input DICOM slices to a sorted 3D numpy array
3. NUMPY_to_DICOM - Converts Numpy images to Dicom datasets and saves them
4. gaussian_filter1d - Creates a 1D Gaussian Filter
5. gaussian_blur3d - Performs 3D Gaussian blur on the input volume
6. preprocessing - Calls DICOM to NUMPY
7. processing - Calls Gaussian blur 3D
8. post_processing - Calls Numpy to DICOM function

## Script 1 (DICOM_to_NUMPY.py)
This script takes in 3 command line arguments:
• --input-dicom, -i - path to input DICOM directory
• --output-npy, -n - path to output numpy file
• --output-json, -j - path to output json file

This script has the following features:
1. Reads the DICOM files in a directory using pydicom.
2. Builds a 3D volume by sorting against each file’s Slice Location DICOM tag in ascending order
3. Normalizes the 3D volume to range between 0 and 1, converting the data from the
input data type to 32-bit float data type
4. Exports pixel data with numpy and the following meta data to a JSON file:
    • Pixel spacing in all three dimensions (they may not be in the same DICOM tag)
    • Series description
    • The imaging modality name (MR, CT, PT, etc.)


To test it, run the below command:

````
python DICOM_to_NUMPY.py -i Data/Full/ -n test1.npy -j test1.json
````


## Script 2 (NUMPY_to_DICOM.py)

This script takes in 3 command line arguments:
• --input-npy, -n - path to input numpy file
• --input-dicom, -d - path to template DICOM directory
• --output-dicom, -o - path to output DICOM directory
This script has the following features:
1. Reads the DICOM files in the directory as a template
2. Reads the image pixel data from the npy file
3. Replaces the pixel data inside the DICOM datasets read in Step 1 with those read at
Step 2
4. Re-scales the pixel values from between 0 to 1 to the dynamic range of the data
type used by the template DICOM files 
5. Assigns a shared new Series Instance UID to all the files, otherwise the new DICOM
files will conflict with the template DICOM files
6. Assigns a new SOP Instance UID to each of the files, so that they can be identified
as new entities in a Picture Archiving and Communication System (PACS).
7. Saves the resulting datasets to the output DICOM folder.


To test it, run the below command,
Please note here to give full path to output test directory. Also, make sure that the directory doesn't exist as I am creating the directory in code.
````
python NUMPY_to_DICOM.py -n test1.npy -d Data\Full\ -o C:\Users\patel\OneDrive\Desktop\SubtleChallenge\subtlechallenge\testdir
````
Script shortcomings: 
1. Full output path file required for DICOM folder Output
2. Directory needs to be non-existent

## config.json
The configuration file is designed in such a way that it can be any dictionary of key value pair, with the key being the DICOM tag and the value being the DICOM tag value.
With these configuration settings, any amount of filtering with the DICOM tags is possible in my code.
I have experimented with Modality but other tags should also work fine.
````
{"Modality":"PT"}
#Try filtering with one of these two dictionaries as your config file.
{"Modality": "MR"}
````

## Workflow.py
This script takes in 3 command line arguments:
•--input-dicom, -i - path to input DICOM directory
• --config, -c - path to the configuration file
• --output-dicom, -o - path to output DICOM directory
This script has the following features:
1. Reads the configuration from the configuration file,
2. Reads all DICOM files from the input directory (and potentially sub-directories),
3. Identifies DICOM series and filter them based on the configuration,
4. Processes the matching DICOM series with the pre-processing, processing, post-processing
5. Saves the processed data to DICOM files in the output DICOM directory.
Note: Script compatible for multiple series

````
python Workflow.py -i Data\ -c config.json -o C:\Users\patel\OneDrive\Desktop\SubtleChallenge\subtlechallenge\output_dir
````

Script shortcomings: 
1. Full output path file required for DICOM folder Output
2. Directory needs to be non-existent


## Docker
Docker is a set of platform as a service products that use OS-level virtualization to deliver
software in packages called containers. The instructions to build a container can be defined
in a Dockerfile, that Dockerfile can be based on any OS depending on the base image you
choose to use and include dependencies needed for the software to run inside the container.

Docker needs to be installed before running the following commands:
To build my container, go to the directory where the Dockerfile is present and open a terminal there. Then run the following commands.

Output PT is the directory which has the outputs copied from the container to the local machine.
````
docker build -t dicom-inference . 
docker run dicom-inference    
docker ps -a  # To get container_name
docker container cp {container_name}:/OutputPT/ OutputPT
````
## Dockerfile Configuration
```
# Base Image: Python
FROM python:latest 

# Working directory set to base directory
WORKDIR /

# Adding files from folder to image
ADD DICOM_to_NUMPY.py  /
ADD NUMPY_to_DICOM.py  /
ADD Workflow.py  /
ADD functions.py  /
ADD config.json /

# Running mkdir command to make Data folder
RUN mkdir Data/
WORKDIR /Data/
ADD Data/ /Data/
WORKDIR /

# Installing packages
RUN pip install pydicom numpy 

# python command to run 
CMD python Workflow.py -i Data -c config.json -o OutputPT
```
## Code design
Code has been designed modularly, with all of the functions found in the functions.py script. The other 3 scripts import the functions from the functions.py script and thus code is reused. Code can handle multiple series at the same time, and each series can be blurred and saved into a folder.