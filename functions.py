
import pydicom
import numpy as np
import os

def dicom_filter(input_dir: str, config: dict) -> list:
    '''Filter DICOM series from the input directory based on a configuration
    :param input_dir: path to the input directory of DICOM files
    :param config: a dict object specifying what DICOM tags & values to use to
    filter the DICOM series
    example: {'Modality': 'MR'}
    :return: a list of matching DICOM series
    '''
    pathsofdicoms=[]
    path=os.getcwd()
    for root, directories, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".dcm"):
                pathsofdicoms.append(os.path.join(root,file))
    #pathsofdicoms is the full list of full paths of each .dcm file
    filtereddicomseries=[]

    # Filtering loops, filters are assumed to be DICOM tags
    for dcmpath in range(len(pathsofdicoms)):
        ds=pydicom.dcmread(pathsofdicoms[dcmpath])
        for i in config:
            if ds.data_element(str(i)).value in config[i]:
                filtereddicomseries.append(pathsofdicoms[dcmpath])
    
    # Returning dictionary with each unique series and corresponding slice paths which passed the filter,Keys:SeriesInstanceUID, Value: List of all paths
    dictionary_to_return={}
    for filteredpath in filtereddicomseries:
        ds=pydicom.dcmread(filteredpath)
        if ds.SeriesInstanceUID in dictionary_to_return:
            dictionary_to_return[ds.SeriesInstanceUID].append(filteredpath)
        if ds.SeriesInstanceUID not in dictionary_to_return:
            dictionary_to_return[ds.SeriesInstanceUID]=[filteredpath]
    return dictionary_to_return

def DICOM_to_NUMPY(input_dicom_dir_list: list) -> np.ndarray:  
    '''Convert the input DICOM slices to a sorted 3D numpy array
    :param input_dicom_dir_list: path to the input directory of DICOM files returned from a value of dicom_filter dictionary
    example: ['/home/x.dcm','/home/data/y.dcm']
    :return: A dictionary which has the Pixel spacing in X,Y and Z , Series Description and Imaging Modality Name and
             the sorted 3D numpy array 
    '''
    arr=[] # Empty list to store the full 3d numpy array
    slice_index=[] # To store the slice indices of each dicom
    for dicomfilenames in input_dicom_dir_list:
        ds=pydicom.dcmread(dicomfilenames)
        arr.append(ds.pixel_array) # Appending the numpy array
        slice_index.append(ds[0x0020,0x0013].value) # Appending the slice number

    arr=np.asarray(arr,dtype=np.float32)
    slice_indices_sorted=np.argsort(np.asarray(slice_index)) # Argsort is used to sort the indices which are then used to sort the numpy array and thus get correct 3D volume
    sorted_pixel_arrays=arr[slice_indices_sorted]
    # Normalization between 0 and 1
    sorted_pixel_arrays=(sorted_pixel_arrays-np.min(sorted_pixel_arrays))/(np.max(sorted_pixel_arrays)-np.min(sorted_pixel_arrays))
    # Reading the pixel spacing value
    pixel_spacing_x=ds[0x0028,0x0030].value[0]
    pixel_spacing_y=ds[0x0028,0x0030].value[1]
    pixel_spacing_z=ds[0x0028,0x0030].value[0]
    # Output dict 
    output_dict = {
    "Pixel spacing in X ": pixel_spacing_x,
    "Pixel spacing in Y": pixel_spacing_y,
    "Pixel spacing in Z": pixel_spacing_z,
    "Series Description": ds.SeriesDescription,
    "Imaging Modality Name": ds.Modality,
    }
    return output_dict, sorted_pixel_arrays


def gaussian_filter1d(size: int,sigma: float) -> np.ndarray:
    '''Creates a 1D Gaussian Filter
    :param size: length of the Gaussian filter
    :param sigma:standard deviation of the filter
    :return: 1D Gaussian filter kernel
    '''
    filter_range = np.linspace(-int(size/2),int(size/2),size)
    gaussian_filter = [1 / (sigma * np.sqrt(2*np.pi)) * np.exp(-x**2/(2*sigma**2)) for x in filter_range] # Gaussian function applied to 1 D array of 5 elements here
    return gaussian_filter

def gaussian_blur_3d(input_3d: np.ndarray, meta_data:dict={'spacing':(2.0,2.0,2.0)}, config:dict={'sigma':2.0},filter_size=5) -> np.ndarray:
    '''Performs 3D Gaussian blur on the input volume
    :param input_3d: input volume in 3D numpy array
    :param meta_data: a dict object with the following key(s):
    'spacing': 3-tuple of floats, the pixel spacing in 3D
    :param config: a dict object with the following key(s):
    'sigma': a float indicating size of the Gaussian kernel in mm.
    :return: the blurred volume in 3D numpy array, same size as input_3d
    '''
    # Since Gaussian function can be applied to each axis independently to get 3D Gaussian blurring, we will convolve with 3 kernels, one along each axis.

    #sigmas for each axis
    sigmax,sigmay,sigmaz=np.asarray(config['sigma'])/np.asarray(meta_data['spacing'])

    gaussian_filter_x=gaussian_filter1d(filter_size,sigmax)
    gaussian_filter_y=gaussian_filter1d(filter_size,sigmay)
    gaussian_filter_z=gaussian_filter1d(filter_size,sigmaz)

    a = np.apply_along_axis(lambda x: np.convolve(x, gaussian_filter_x, mode='same'), 0, input_3d)
    a= np.apply_along_axis(lambda x: np.convolve(x, gaussian_filter_y, mode='same'), 1, a)
    blurred_volume= np.apply_along_axis(lambda x: np.convolve(x, gaussian_filter_z, mode='same'), 2, a)

    return blurred_volume


def NUMPY_to_DICOM(np_array:np.ndarray,input_dicom_dir:list, output_dicom_dir="Output"):
    '''Convert Numpy images to Dicom datasets and saves them
    :param np_array: processed 3D NP array
    :param input_dicom_dir: path to the input directory of DICOM files returned from a value of dicom_filter dictionary (list of individual paths)
    :param output_dicom_dir: Name of the folder in which the new dicoms will get stored
    '''
    path=os.getcwd()
    os.mkdir(output_dicom_dir)
    # Unique Series ID
    Series_ID=pydicom.uid.generate_uid()
    for i,dicomfilenames in enumerate(input_dicom_dir):
        ds=pydicom.dcmread(dicomfilenames)
        # Multiplying by 32767 to scale back to int 16 values
        ds.PixelData=((np_array[i]*32767).astype("int16")).tobytes()
        # SOP instance ID
        ds[0x0008,0x0018].value=pydicom.uid.generate_uid()
        ds[0x0020,0x000E].value=Series_ID
        # Saving the dataset into new files
        ds.save_as(os.path.join(output_dicom_dir,"{}output{}.dcm".format(Series_ID,i+1)))
    return


def preprocessing(input_dicom_list) -> np.ndarray:
    '''Preprocessing; calls DICOM to NUMPY
    :param input_dicom_list: path to the input directory of DICOM files returned from a value of dicom_filter dictionary
    :return : A dictionary which has the Pixel spacing in X,Y and Z , Series Description and Imaging Modality Name and
             the sorted 3D numpy array 
    '''
    output_dict,numpy_array=DICOM_to_NUMPY(input_dicom_list)
    return output_dict,numpy_array

def processing(numpy_array:np.ndarray, dict1:dict={'spacing':(2.0,2.0,2.0)} , dict2:dict={'sigma':2.0},filter_size:int=5) -> np.ndarray:
    '''Processing; calls Gaussian blur 3D
    :param input_3d: input volume in 3D numpy array
    :param meta_data: a dict object with the following key(s):
    'spacing': 3-tuple of floats, the pixel spacing in 3D
    :param config: a dict object with the following key(s):
    'sigma': a float indicating size of the Gaussian kernel in mm.
    :return: the blurred volume in 3D numpy array, same size as input_3d
    ''' 
    return gaussian_blur_3d(numpy_array,dict1,dict2,filter_size)

def post_processing(numpy_array:np.ndarray, input_dicom_dir:list, output_dicom_dir:str)-> None:
    '''Post-Processing; calls Numpy to DICOM function
    :param np_array: processed 3D NP array
    :param input_dicom_dir: path to the input directory of DICOM files returned from a value of dicom_filter dictionary (list of individual paths)
    :param output_dicom_dir: Name of the folder in which the new dicoms will get stored
    ''' 
    NUMPY_to_DICOM(numpy_array, input_dicom_dir, output_dicom_dir)
    return