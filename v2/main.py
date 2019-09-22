import json


class SettingsManager:
    config_file = None

    def __init__(self, json_config_file):
        self.config_file = json_config_file

    with open(f'{config_file}') as config_file:
        settings = json.load(config_file)

    extensions = settings['extension']
