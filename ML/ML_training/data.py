#data.py
import pandas as pd

def read_action_data(action, files):
    """Import datafiles of a certain action of format '[action]_[File number]

        Args:
            action (string): name of action in file name
            files(int): number of files to import


        Returns:
            dataframe: dataframe of raw readings for the specified action

        """

    data_list = []
    
    file_name = action + "_%d.csv"
    for i in range(files):
        df = pd.read_csv (file_name%i)
        data_list.append(df)
    consolidated = pd.concat(data_list)
    consolidated['Action']=action
    return consolidated
  
def raw_to_df(files):
    """Import datafiles of all actions and walk/non-action

        Args:
            files(int): number of files to import


        Returns:
            grenade (dataframe): dataframe of raw readings for grenade action
            shield (dataframe): dataframe of raw readings for shield action
            quit (dataframe): dataframe of raw readings for quit action
            reload (dataframe): dataframe of raw readings for reload action
            walk (dataframe): dataframe of raw readings for walk/non-action
            consolidated (dataframe): dataframe of raw readings for all 4 actions

        """
    grenade = read_action_data('grenade', files)
    shield = read_action_data('shield', files)
    quit =  read_action_data('quit', files)
    reload = read_action_data('reload', files)
    walk = read_action_data('walk', files)
    consolidated = pd.concat([grenade,shield,quit,reload])
    return (grenade,shield,quit,reload,walk,consolidated)
