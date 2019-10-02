import json
import os

# print("==== BEM VINDO AO SEU ARQUIVO MAIN.PY ====")

class ConfigManager:
    # config_file = None

    def __init__(self, config_file_json):
        self.config_file = config_file_json
        

    @property
    def workdir(self):
        return os.getcwd()

    @property
    def settings(self):
        with open(self.config_file) as config_file:
            settings = json.load(config_file)
        return settings



# table_path = '/home/dariodg/Desktop/Free/Galpao/ComissionApp/docs/comissabril2019.XLS'
