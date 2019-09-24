import pandas as pd
from configuration import SettingsManager
import json

# df = pd.read_excel('/home/dariodg/Desktop/Free/Galpao/ComissionApp/docs/comissabril2019.XLS')


class DataEngineer:

    CONFIG_FILE = 'general_config.json'
    SETTINGS = SettingsManager(CONFIG_FILE)
    DATA = pd.read_excel(SETTINGS['data_file'])

    # def __init__(self, config_file):
    #     self.settings = SettingsManager(config_file)
    #     self.data_file = pd.read_excel(self.settings['data_file'])

    @property
    def data_info(self):
        return f'''
            "config_file": {self.CONFIG_FILE},
            "config_keys": {tuple(self.SETTINGS.keys())},
            "config_values": {tuple(self.SETTINGS.values())},
            "data_file": {self.SETTINGS["data_file"]}
        '''

    def fill_sem_turma(value):
        """ Change empty values, considered as float, to 'sem_turma' """
        if type(value) == float:
            return 'sem_turma'
        return value
    
    def run(self):
        """ Apply the treatments in the table and return a new dataframe"""
        turmas = self.DATA['turma'].apply(self.fill_sem_turma)
        
        treated_df = {
            'turma': turmas
        }
        return pd.DataFrame(data=treated_df)

# CONFIG_FILE = 'general_config.json'
# SETTINGS_MANAGER = SettingsManager(CONFIG_FILE)
# DATA = SETTINGS_MANAGER.settings

# print(f'''
#             "data_file": {CONFIG_FILE},
#             "data_keys":{tuple(DATA.keys())},
#             "data_values":{tuple(DATA.values())}
#         ''')

print(DataEngineer().run().head())