import pandas as pd
import json
import re

from config_manager import ConfigManager


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
    def fill_empty(current_value, new_value):
        """ Change empty values, considered as float, to new_value """
        if type(current_value) == float:
            return new_value
        return current_value

    @staticmethod
    def str_normalize(row):
        return row.upper()
    
    @staticmethod
    def strip_n_split(row, separator):
        """Remove white spaces and split new lines, forming a list."""
        return row.strip().split(separator)

    @staticmethod
    def get_match(row, pattern):
        """ 
        Select a value from a list that correspond to a given value, or
        returns empty if no match was found.
        PS: Assign the result to a new variable. Dont override the original
         """
        for value in row:
            if pattern in value:
                return value
        return ''

    def _arrange_patterns(self):
        """Builds a regex for get_non_match method. Ex: '(ADES)|(MULT)|(PROD)'."""
        patterns = self.SETTINGS['classification_patterns']
        all_patterns = []
        for pattern in patterns.values():
            all_patterns.append(f'({pattern})')
        return '|'.join(all_patterns)

    @staticmethod
    def _str_to_float(float_string):
        """
        It takes a float string ("1,23" or "1,234.567.890") and
        converts it to floating point number (1.23 or 1.234567890).
        """
        
        if float_string is not None: 
            float_string = str(float_string)
            if float_string.count(".") == 1 and float_string.count(",") == 0:
                return float(float_string)
            else:
                midle_string = list(float_string)
                while midle_string.count(".") != 0:
                    midle_string.remove(".")
                out_string = str.replace("".join(midle_string), ",", ".")
            return float(out_string)
        return ''

    def get_non_match(self, row):
        """Select a value from a list that do not correspond a given regex"""
        regex = self._arrange_patterns()
        for value in row:
            if bool(re.search(regex, value)):
                return ''
            return value


    def info_n_amount(self, pd_serie):
        df = pd_serie.str.split(pat=r'R\$', expand=True)
        df[0] = df[0].str.strip()
        df[1] = df[1].str.strip()
        df[1] = df[1].apply(self._str_to_float)
        return df[0], df[1]

    def apply_treatment(self):
        """ 
        Main method of the class.
        Called to apply the functions, through pandas, and return a new dataframe.
        """

        # Column 'turma' treatment
        turmas = self.DATASET['turma'].apply(self.fill_empty, args=('sem_turma',))

        # Normalize descritivo column and split each line row string in a list of values.
        descritivo = self.DATASET['descritivo'].apply(self.str_normalize)
        descritivo = descritivo.apply(self.strip_n_split)

        # Select values of a panda.Series that match a criteria.
        adesao = descritivo.apply(self.get_match, args=('ADES',))
        producao = descritivo.apply(self.get_match, args=('PROD',))
        multa = descritivo.apply(self.get_match, args=('MULT',))
        desconto = descritivo.apply(self.get_match, args=('DESC',))

        # Select values of a panda.Series that dont match a criteria.
        parcelas = descritivo.apply(self.get_non_match)

        treated_df = {
            'turma': turmas
        }
        
        return treated_df

    def export_xls(self):
        """ Export the treated dataframe to a excel file """
  
        pass
