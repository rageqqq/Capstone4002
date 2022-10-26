#feature.py
from scipy import stats
import numpy as np
from math import sqrt
from model import bias_to_cpp

def split_samples(combined_raw, timesteps):
    """splits raw data into samples of size timestep

        generates extra samples using partial action data with 59 timestep overlap. 

        Args:
            combined_raw (dataframe): raw readings of all actions
            timesteps(int): number of timesteps in each sample


        Returns:
            segments(list): samples extracted for feature extraction
            labels(list):   the coresponding labels for the extracted samples

        """

    segments = []
    labels = []
    N_TIME_STEPS = timesteps
    for i in range(0, len(combined_raw) - N_TIME_STEPS):
        ax = combined_raw['AccX'].values[i: i + N_TIME_STEPS]
        ay = combined_raw['AccY'].values[i: i + N_TIME_STEPS]
        az = combined_raw['AccZ'].values[i: i + N_TIME_STEPS]
        gx = combined_raw['GyroX'].values[i: i + N_TIME_STEPS]
        gy = combined_raw['GyroY'].values[i: i + N_TIME_STEPS]
        gz = combined_raw['GyroZ'].values[i: i + N_TIME_STEPS]
        label = stats.mode(combined_raw['Action'][i: i + N_TIME_STEPS])[0][0]
        segments.append([ax, ay, az, gx, gy, gz])
        labels.append(label)
    return (segments, labels)

def Mean(data):
    """Returns the mean of a time series"""
    return data.mean()

def Median(data):
    """Returns the median of a time series"""
    return data.median()


def extract_acc_magnitude(data):
    """extract the magnitude of acceleration data 

        Args:
            data (list): list of sample raw data

        Returns:
            list: array of magnitudes

        """
    mag_array = []
    for i in range(len(data)):
        mags = []
        for t in range(len(data[i][0])): 
            mags.append( sqrt( data[i][0][t]**2 + data[i][1][t]**2 + data[i][2][t]**2) )
        mag_array.append(mags)
    return mag_array

def extract_acc_median(data):

    """extract the median of acceleration data 

        Args:
            data (list): list of sample raw data

        Returns:
            tuple: tuple of median data of acc x,y,z

        """

    median_array = []

    for i in range(len(data)):
        median_array.append([np.median(data[i][0]), np.median(data[i][1]), np.median(data[i][2])])
    return median_array

def extract_gyro_median(data):
    """extract the median of gyro data 

        Args:
            data (list): list of sample raw data

        Returns:
            tuple: tuple of median data of gyro x,y,z

        """

    median_array = []

    for i in range(len(data)):
        median_array.append([np.median(data[i][3]), np.median(data[i][4]), np.median(data[i][5])])
    return median_array


def extract_acc_mean(data):
    """extract the mean of acceleration data 

        Args:
            data (list): list of sample raw data

        Returns:
            tuple: tuple of mean data of acc x,y,z

        """
    mean_array = []

    for i in range(len(data)):
        mean_array.append([Mean(data[i][0]),Mean(data[i][1]),Mean(data[i][2])])
    return mean_array

def extract_gyro_mean(data):
    """extract the mean of gyro data 

        Args:
            data (list): list of sample raw data

        Returns:
            tuple: tuple of mean data of gyro x,y,z

        """
    mean_array = []

    for i in range(len(data)):
        mean_array.append([Mean(data[i][3]),Mean(data[i][4]),Mean(data[i][5])])
    return mean_array

#2-181 acc, 182-361 gyro, 362-364 mean_a, 365-367 mean_g, 368-370 median_a, 371-373 median_g, 374-433 mag_a 
#acc mean -0.205, 0.628, 0.331
#gyro mean -0.02446,-0.274, 0.18607
#acc median 0.395, 0.66567, 0.1941
#gyro median -0.24592, .086605, -0.01507
def merge_feature_array(raw, mean_a, mean_g, median_a, median_g, mag):
    """Merge all extracted features and raw data into one sample 
        0-179 acc, 180-359 gyro, 360-362 mean_a, 363-365 mean_g, 366-368 median_a, 369-371 median_g, 372-431 mag_a

        Args:
            raw (list): list of sample raw data
            mean_a (list): list of extracted sample acceleration means
            mean_g (list): list of extracted sample gyro means
            median_a (list): list of extracted sample acceleration meedians
            median_g (list): list of extracted sample gyro medians
            mag (list): list of extracted sample acceleration magnitudes
        

        Returns:
            list: list of flattened samples
        """
    out = []
    raw = np.array(raw)
    for i in range(len(raw)):
        arr1 = np.concatenate((raw[i].flatten(), mean_a[i]))
        arr2 = np.concatenate((arr1, mean_g[i]))
        arr3 = np.concatenate((arr2, median_a[i]))
        arr4 = np.concatenate((arr3, median_g[i]))
        arr5 = np.concatenate((arr4,mag[i]))
        out.append(arr5)

    return out

def extract_features(data):
    """extract features from data
        0-179 acc, 180-359 gyro, 360-362 mean_a, 363-365 mean_g, 366-368 median_a, 369-371 median_g, 372-431 mag_a

        Args:
            data (list): list of sample raw data  

        Returns:
            list: list of flattened samples
        """
    raw = data
    mean_a = extract_acc_mean(data)
    mean_g = extract_gyro_mean(data)
    median_a = extract_acc_median(data)
    median_g = extract_gyro_median(data)
    mag = extract_acc_magnitude(data)
    return merge_feature_array(raw,mean_a,mean_g,median_a,median_g,mag)

def label_index(labels, one_hot):
    """Label the corresponding classification index

        Args:
            labels (list): list of string labels
            one_hot(list): list of one hot encoded labels
        """
    def find_index(index):
        for i in range(len(one_hot)):
            if one_hot[i][index] == 1:
                return (labels[i], index, one_hot[i])
    for i in range(4):
        print("%s -  index: %s, one hot: %s"%(find_index(i)))

def generate_test(segments, one_hot):
    """extracts samples of each class for use in hls testing

        Args:
            segments (list): list of samples
            one_hot(list): list of one hot encoded labels
        
        Returns:
            list: list of one sample from each class
        """
    samples = []
    def find_index(index):
        for i in range(len(one_hot)):
            if one_hot[i][index] == 1:
                return segments[i]
    for i in range(4):
        samples.append(find_index(i))
    return samples

def save_test(segments, one_hot):
    """extracts samples of each class for use in hls testing and writes to txt file in c format

        Args:
            segments (list): list of samples
            one_hot(list): list of one hot encoded labels
        """
    samples = generate_test(segments, one_hot)
    test_inputs = "float test_input[INPUT_LAYER*NO_OF_TESTCASE] = " + bias_to_cpp(samples)
    file = open("test.txt", "w+")
    file.write(test_inputs)
    file.close()