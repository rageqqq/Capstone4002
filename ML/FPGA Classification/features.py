from math import sqrt
from numpy import mean, median, std, percentile, fft, abs, argmax
import numpy as np


#do corellation check for features
#COllect a variety of data (must be natural)
def Mean(data):
    """Returns the mean of a time series"""
    return data.mean()


def Median(data):
    """Returns the median of a time series"""
    return data.median()


def extract_acc_magnitude(data):
    """Extract acc magnitude data from sliding window.

    Output is in the form Acc_Mag * 60

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        list: list of 60 mag values

    """
    mag_array = []
    for i in range(len(data)):
        mag_array.append(sqrt(data[i][0]**2 + data[i][1]**2 + data[i][2]**2))
    return mag_array


def extract_acc_median(data):
    """Extract acc median data from sliding window.

    Output is in the form Mean_Acc_x, Mean_Acc_y, Mean_Acc_z

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        list: list of 3 median values

    """
    transpose = np.array(data).transpose()
    median_array = [np.median(transpose[0]), np.median(
        transpose[1]), np.median(transpose[2])]
    return median_array


def extract_gyro_median(data):
    """Extract gyro data from sliding window.

    Output is in the form Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        list: list of 3 mean values

    """
    transpose = np.array(data).transpose()
    median_array = [np.median(transpose[3]), np.median(
        transpose[4]), np.median(transpose[5])]
    return median_array


def extract_acc_mean(data):
    """Extract acc mean data from sliding window.

    Output is in the form Mean_Acc_x, Mean_Acc_y, Mean_Acc_z

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        list: list of 3 mean values

    """
    transpose = np.array(data).transpose()
    mean_array = [Mean(transpose[0]), Mean(transpose[1]), Mean(transpose[2])]
    return mean_array


def extract_gyro_mean(data):
    """Extract gyro mean data from sliding window.

    Output is in the form Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        list: list of 3 mean values

    """
    transpose = np.array(data).transpose()
    mean_array = [Mean(transpose[3]), Mean(transpose[4]), Mean(transpose[5])]
    return mean_array


def merge_feature_array(raw, mean_a, mean_g, median_a, median_g, mag):
    """Merge all the extracted feature arrays.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        raw (list): The window to extract feature from of shape (60,6)
        mean_a (list): The acc means extracted from raw in the shape (3,)
        mean_g (list): The gyro means extracted from raw in the shape (3,)
        median_a (list): The acc medians extracted from raw in the shape (3,)
        median_g (list): The gyro medians extracted from raw in the shape (3,)
        mag (list): The acceleration magnitudesextraced from raw in the shape (60,)

    Returns:
        list: list of 432 timeseries features for classification

    """
    
    out = []
    raw = np.array(raw)
    transpose = raw.transpose()
    arr1 = np.concatenate((transpose.flatten(), mean_a))
    arr2 = np.concatenate((arr1, mean_g))
    arr3 = np.concatenate((arr2, median_a))
    arr4 = np.concatenate((arr3, median_g))
    arr5 = np.concatenate((arr4, mag))
    out.append(arr5)

    return out


def extract_features(data):
    """Extract 432 time series data features from sliding window.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        Array: np array of 432 timeseries features for classification

    """

    raw = data
    mean_a = extract_acc_mean(data)
    mean_g = extract_gyro_mean(data)
    median_a = extract_acc_median(data)
    median_g = extract_gyro_median(data)
    mag = extract_acc_magnitude(data)
    return np.array(merge_feature_array(raw, mean_a, mean_g, median_a, median_g, mag))


def extract_features_v2(data):
    """Extract 192 time series data features from sliding window.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        Array: np array of 432 timeseries features for classification

    """

    raw = data
    mean_a = extract_acc_mean(data)
    mean_g = extract_gyro_mean(data)
    median_a = extract_acc_median(data)
    median_g = extract_gyro_median(data)
    return np.array(merge_feature_array_v2(raw, mean_a, mean_g, median_a, median_g))


def extract_features_v3(data):
    """Extract 432 time series data features from sliding window.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        data (list): The window to extract feature from of shape (60,6)

    Returns:
        Array: np array of 432 timeseries features for classification

    """

    raw = data
    mean_a = extract_acc_mean(data)
    mean_g = extract_gyro_mean(data)
    median_a = extract_acc_median(data)
    median_g = extract_gyro_median(data)

    return np.array(merge_feature_array_v3(raw, mean_a, mean_g, median_a, median_g))


def merge_feature_array_v2(raw, mean_a, mean_g, median_a, median_g):
    """Merge all the extracted feature arrays.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        raw (list): The window to extract feature from of shape (60,6)
        mean_a (list): The acc means extracted from raw in the shape (3,)
        mean_g (list): The gyro means extracted from raw in the shape (3,)
        median_a (list): The acc medians extracted from raw in the shape (3,)
        median_g (list): The gyro medians extracted from raw in the shape (3,)
        mag (list): The acceleration magnitudesextraced from raw in the shape (60,)

    Returns:
        list: list of 432 timeseries features for classification

    """
    
    out = []
    raw = np.array(raw)
    transpose = raw.transpose()
    transpose = transpose[:3]
    arr1 = np.concatenate((transpose.flatten(), mean_a))
    arr2 = np.concatenate((arr1, mean_g))
    arr3 = np.concatenate((arr2, median_a))
    arr4 = np.concatenate((arr3, median_g))
    out.append(arr4)

    return out


def merge_feature_array_v3(raw, mean_a, mean_g, median_a, median_g):
    """Merge all the extracted feature arrays.

    Output is in the form  Acc_x * 60, Acc_y * 60, Acc_z * 60, Gyro_x * 60, Gyro_y * 60, Gyro_z * 60, Mean_Acc_x, Mean_Acc_y, Mean_Acc_z, Mean_Gyro_x, Mean_Gyro_y, Mean_Gyro_z, Median_Acc_x, Median_Acc_y, Median_Acc_z, Median_Gyro_x, Median_Gyro_y, Median_Gyro_z, Mag_Acc * 60

    Args:
        raw (list): The window to extract feature from of shape (60,6)
        mean_a (list): The acc means extracted from raw in the shape (3,)
        mean_g (list): The gyro means extracted from raw in the shape (3,)
        median_a (list): The acc medians extracted from raw in the shape (3,)
        median_g (list): The gyro medians extracted from raw in the shape (3,)
        mag (list): The acceleration magnitudesextraced from raw in the shape (60,)

    Returns:
        list: list of 432 timeseries features for classification

    """
    
    out = []
    raw = np.array(raw)
    transpose = raw.transpose()
    arr1 = np.concatenate((transpose.flatten(), mean_a))
    arr2 = np.concatenate((arr1, mean_g))
    arr3 = np.concatenate((arr2, median_a))
    arr4 = np.concatenate((arr3, median_g))
    out.append(arr4)

    return out