import pandas as pd
from config_manager import ConfigManager
import json


class DataEngineer:

    CONFIG_FILE = 'general_config.json'
    SETTINGS = ConfigManager(CONFIG_FILE).settings
    # this line will be replaced by the gui input
    DATASET = pd.read_excel(SETTINGS['dataset'])

    # def __init__(self, config_file):
    #     self.settings = ConfigManager(config_file)
    #     self.data_file = pd.read_excel(self.settings['data_file'])

    @property
    def data_info(self):
        return f'''
            "config_file": {self.CONFIG_FILE},
            "config_keys": {tuple(self.SETTINGS.keys())},
            "config_values": {tuple(self.SETTINGS.values())},
            "data_file": {self.SETTINGS["data_file"]}
        '''

    @staticmethod
    def fill_values(current_value, new_value):
        """ Change empty values, considered as float, to new_value """
        if type(current_value) == float:
            return new_value
        return current_value

    @staticmethod
    def str_normalize(row):
        return row.upper()
    
    @staticmethod
    def strip_n_split(row):
        """ Remove white spaces and split new lines, forming a list"""
        return row.strip().split('\n')

    @staticmethod
    def get_match(row, pattern):
        """ 
        Search for a pattern within the values of a row(type list) and return the value
        if the match is True, else returns empty.
        Assign the result to a new variable. Dont override the original
         """
        for value in row:
            if pattern in value:
                return value
        return ''

    def apply_treatment(self):
        """ 
        Main method of the class.
        Called to apply the functions, through pandas, and return a new dataframe.
        """

        """ Column 'turma' treatment """
        turmas = self.DATASET['turma'].apply(self.fill_values, args=('sem_turma',))

        """ Column 'descritivo' treatment """
        descritivo = self.DATASET['descritivo'].apply(self.str_normalize)
        descritivo = descritivo.apply(self.strip_n_split)

        """ Schema for the treated dataframe """
        treated_df = {
            'turma': turmas
        }
        return pd.DataFrame(data=treated_df)
