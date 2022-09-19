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