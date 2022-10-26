# data_analysis.py
import numpy as np
import pandas as pd

# Data Analysis for activity detection


def plot_columns(column_name, grenade, shield, quit, reload, walk):
    """Data Analysis for activity detection

        plots the various actions in a graph for activity detection analysis

        Args:
            column_name (string): name of the 1 of 6 columns to plot
            grenade (dataframe): dataframe of grenade action
            shield (dataframe): dataframe of shield action
            quit (dataframe): dataframe of quit action
            reload (dataframe): dataframe of reload action
            walk (dataframe): dataframe of walk action
    """
    grenade[[column_name]].plot()
    shield[[column_name]].plot()
    quit[[column_name]].plot()
    reload[[column_name]].plot()
    walk[[column_name]].plot()

# Double check activity detection threshold
def sample_splitter(data, timesteps):
    """Splits data into samples of the specified number of timesteps

        Args:
            data (list): raw_values
            timesteps(int): number of timesteps in each sample

        Returns:
            list: list of samples of size timesteps

        """
    samples = []
    for i in range(int(data.size/timesteps)):
        temp = data[i:i+timesteps]
        samples.append(temp)
    return samples

# y of non action seems to always be negative
def activity_checker(samples, threshold):
    """Returns how many time certain axis in a sample is above a certain threshold

        Args:
            samples (list): list of samples
            threshold(float): threshold to monitor 

        Returns:
            int: number of times the sample goes above the threshold

        """
    a_level = 0
    for z in range(len(samples)):
        if samples[z]>threshold:
            a_level+=1


    return a_level


def max_act_checker(samples, threshold):
    """Returns highest number of readings above threshold in all the samples

        Args:
            samples (list): list of samples
            threshold(float): threshold to monitor 

        Returns:
            int: highest number of readings above threshold in all the samples

        """
    highest = -100
    for t in range(len(samples)):
        sample = samples[t]
        c_act = activity_checker(sample, threshold)
        if highest == -100:
            highest = c_act
        elif c_act > highest:
            highest = c_act
    return str(highest)

def min_act_checker(samples, threshold):
    """Returns lowest number of readings above threshold in all the samples

        Args:
            samples (list): list of samples
            threshold(float): threshold to monitor 

        Returns:
            int: lowest number of readings above threshold in all the samples

        """
    lowest = 100
    for t in range(len(samples)):
        sample = samples[t]
        c_act = activity_checker(sample,threshold)
        if lowest == 100:
            lowest = c_act
        elif c_act < lowest:
            lowest = c_act
    return str(lowest)

def column_values(data, column_name):
    """Extract column of a dataframe as a 1d array

        Args:
            data (dataframe): list of samples
            column_name(string): name of column to extract

        Returns:
            np.array: Column of a dataframe as a 1d np array

        """
    return data[[column_name]].values

def act_range_checker(data, timesteps, column_name, threshold):
    """Checks the min anx max 

        Args:
            data (dataframe): list of samples
            timesteps(int): number of timesteps in each sample
            column_name(string): name of column to extract
            threshold(float): threshold to monitor 

        Returns:
            string: min and max values in samples that hit threshold

        """
    arr = column_values(data, column_name)
    samples = sample_splitter(arr,timesteps)
    min = min_act_checker(samples,threshold)
    max = max_act_checker(samples,threshold)
    return " Min: %s, Max: %s"%(min, max)


def get_corr(extracted, labels, threshold):
    """Checks the min anx max 

        Args:
            extracted (list): list of samples with features extracted
            labels(string): list of labels for each sample
            threshold(float): correlation threshold to monitor

        """
    test = pd.DataFrame(np.array(extracted))
    labels_test = pd.DataFrame(np.array(labels))
    labels_test.columns = ["Action"]
    corr = pd.concat([test,labels_test], axis=1)
    corr['Action'] = pd.Categorical(corr['Action'])
    corr['action'] = corr['Action'].cat.codes
    action_corr = corr.corr().iloc[432].to_numpy()

    columns = []
    acc_x = True
    acc_y = True
    acc_z = True
    g_x = True
    g_y = True
    g_z = True
    mag = True
    for i in range(len(action_corr)):
        if action_corr[i] >=threshold or action_corr[i] <= -threshold:
            if i <60 and acc_x:
                print("accx: %s"%action_corr[i])
                acc_x = False
                columns.append(i+1)
            elif i >=60 and i <120 and acc_y:
                print("accy: %s"%action_corr[i])
                acc_y = False
                columns.append(i+1)
            elif i >=120 and i <180 and acc_z:
                print("accz: %s"%action_corr[i])
                acc_z = False
                columns.append(i+1)
            elif i >=180 and i <240 and g_x:
                print("gyrox: %s"%action_corr[i])
                g_x = False
                columns.append(i+1)
            elif i >=240 and i <300 and g_y:
                print("gyroy: %s"%action_corr[i])
                g_y = False
                columns.append(i+1)
            elif i >=300 and i <360 and g_z:
                print("gyroz: %s"%action_corr[i])
                g_z = False
                columns.append(i+1)
            elif i >=360 and i <372:
                columns.append(i+1)
                if(i== 360):
                    print("acc mean x: %s"%(action_corr[i]))
                if(i == 361):
                    print("acc mean y: %s"%action_corr[i])
                if(i == 362):
                    print("acc mean z: %s"%action_corr[i])
                if(i == 363):
                    print("gyro mean x: %s"%action_corr[i])
                if(i == 364):
                    print("gyro mean y: %s"%(action_corr[i]))
                if(i== 365):
                    print("gyro mean z: %s"%action_corr[i])
                if(i == 366):
                    print("acc median x: %s"%action_corr[i])
                if(i == 367):
                    print("acc median y: %s"%action_corr[i])
                if(i == 368):
                    print("acc median z: %s"%action_corr[i])
                if(i == 369):
                    print("gyro median x: %s"%action_corr[i])
                if(i == 370):
                    print("gyro median y: %s"%action_corr[i])
                if(i== 371):
                    print("gyro median z: %s"%action_corr[i]) 
            elif i >=372 and i < 432 and mag:
                mag = False
                columns.append(i+1)
                print("mag: %s"%action_corr[i])

