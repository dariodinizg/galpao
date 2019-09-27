import pandas as pd
import json
import re

from config_manager import ConfigManager


class DataEngineer:

    CONFIG_FILE = 'general_config.json'
    SETTINGS = ConfigManager(CONFIG_FILE).settings
    # this line will be replaced by the gui input
    DATASET = pd.read_excel(SETTINGS['dataset'])
    PATTERNS = SETTINGS['classification_patterns']

    def _regex_build(self):
        """Builds a regex for get_non_match method. Ex: '(ADES)|(MULT)|(PROD)'."""
        all_patterns = []
        for pattern in self.PATTERNS.values():
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
            if bool(re.search(pattern, value)):
                return value
        return ''

    def get_non_match(self, pd_serie):
        """Select a value from a list that do not correspond a given regex"""
        regex = re.compile('(ADES)|(MULT)|(PROD)|(DESC)')
        valids = []
        for row in pd_serie:
            invalid = []
            row_valid = []
            for value in row:
                if not bool(regex.search(value)):
                    row_valid.append(value)
                else:
                    invalid.append(value)
            if len(invalid) == len(row):
                row_valid.append('')
            valids.append(row_valid) # Creates a nested list

        """
        Since might be more than one payment of type 'parcelas' for a client, 
        the code below check the valids list for two or more matches and rebuild the string
        concatenating each label - colon separator - with the sum the amount of all values, 
        thus creating one line for label and amount, keeping the dataframe consistency.
        """
        treated_valid = []
        for value in valids:
            if value != '':
                if len(value) == 1: 
                    treated_valid.append(*value) # Descompact the nested list
                else:
                    info_to_join = []
                    amount_to_join = []
                    for item in value:
                        info, amount = item.split(r'R$')
                        info_to_join.append(info)
                        amount_to_join.append(self._str_to_float(amount))
                    info_joined = ','.join(info_to_join)
                    amount_sum = sum(amount_to_join)
                    treated_valid.append(f"{info_joined} R$ {amount_sum}")
            else:
                treated_valid.append('')
                
        return treated_valid

    def split_label_n_amount(self, pd_serie):
        """ Split the payment's label and its amount in two columns."""
        df = pd_serie.str.split(pat=r'R\$', expand=True)
        df[0] = df[0].str.strip()
        df[1] = df[1].str.strip()
        df[1] = df[1].apply(self._str_to_float)
        return df[0], df[1]

    def parcelas_split_label_n_amount(self, list_obj: list):
        """ 
        Split the payment's label and its amount in two columns.
        It needs a different function for split label and amount since the 
        parameter is not a panda.Series, but a python list.
        """
        label_list = []
        amount_list = []
        for value in list_obj:
            if value != '':
                label,amount = value.split('R$')
                label_list.append(label)
                amount_list.append(amount)
            else:
                label_list.append('')
                amount_list.append('')
        return label_list, amount_list

    def apply_treatment(self):
        """ 
        Main method of the class.
        Called to apply the functions, through pandas, and return a new dataframe.
        """

        # Column 'turma' treatment
        turmas = self.DATASET['turma'].apply(self.fill_empty, args=('sem_turma',))

        # Normalize descritivo column and split each line row string in a list of values.
        descritivo = self.DATASET['descritivo'].apply(self.str_normalize)
        descritivo = descritivo.apply(self.strip_n_split, args=('\n',))

        # Select values of a panda.Series that dont match a criteria.
        parcelas = pd.Series(data=self.get_non_match(descritivo))
        
        # Select values of a panda.Series that match a criteria.
        adesao = descritivo.apply(self.get_match, args=(self.PATTERNS['adesao'],))
        producao = descritivo.apply(self.get_match, args=(self.PATTERNS['producao'],))
        multa = descritivo.apply(self.get_match, args=(self.PATTERNS['multa'],))
        desconto = descritivo.apply(self.get_match, args=(self.PATTERNS['desconto'],))

        # Split label and amount
        label_parcelas, amount_parcelas = self.parcelas_split_label_n_amount(parcelas)
        label_producao, amount_producao = self.split_label_n_amount(producao)
        label_multa, amount_multa = self.split_label_n_amount(multa)
        label_desconto, amount_desconto = self.split_label_n_amount(desconto)
        label_adesao, amount_adesao = self.split_label_n_amount(adesao)
  
        
        treated_df = {
            'TURMA': turmas,
            'TITULO': self.DATASET['titulo'],
            'VENCIMENTO': self.DATASET['vencimento'],
            'SACADO': self.DATASET['sacado'],
            'VAL_RECEBIDO':self.DATASET['recebido'],
            'VAL_PARCELA': amount_parcelas,
            'VAL_PRODUCAO': amount_producao,
            'VAL_MULTA': amount_multa,
            'VAL_DESCONTO': amount_desconto,
            'VAL_ADESAO': amount_adesao,
            'DATA_CREDITO':self.DATASET['credito'],

        }
        
        return treated_df

    def export_excel(self):
        """ Export the treated dataframe to a excel file """
        df = pd.DataFrame(data=self.apply_treatment())
        defaul_save_names = self.SETTINGS['default_save_name']
        if True:
            df.to_excel(defaul_save_names['incomes_table'], index=False)

    def run(self):
        """ Main method to treat and export the data"""
        self.apply_treatment()
        self.export_excel()


if __name__ == '__main__':
    DataEngineer().run()
    # DataEngineer().apply_treatment()
    # DataEngineer()._regex_build()