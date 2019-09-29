import pandas as pd
import json
import re
from numpy import nan

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

        if bool(float_string) is not False: 
            float_string = str(float_string).replace(' ','')
            if float_string.count(".") == 1 and float_string.count(",") == 0:
                return float(float_string)
            else:
                midle_string = list(float_string)
                while midle_string.count(".") != 0:
                    midle_string.remove(".")
                out_string = str.replace("".join(midle_string), ",", ".")
            return float(out_string)
        return 0

    @staticmethod
    def fill_empty(current_value, new_value):
        """ Change empty values, considered as float, to new_value """
        if str(current_value) == 'nan':
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
        return 0

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
                row_valid.append(0)
            valids.append(row_valid) # Creates a nested list

        """
        Since might be more than one payment of type 'parcelas' for a client, 
        the code below check the valids list for two or more matches and rebuild the string
        concatenating each label - colon separator - with the sum the amount of all values, 
        thus creating one line for label and amount, keeping the dataframe consistency.
        """
        treated_valid = []
        for value in valids:
            if value != 0:
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
                treated_valid.append(0)
                
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
            if type(value) != int:
                label,amount = value.split('R$')
                label_list.append(label)
                amount_list.append(amount)
            else:
                label_list.append('')
                amount_list.append(0)
        return label_list, amount_list

    def apply_treatment(self):
        """ 
        Main method of the class.
        Called to apply the functions, through pandas, and return a new dataframe.
        """

        # Column 'turma' treatment
        # turmas = self.DATASET['turma'].apply(self.fill_empty, args=('sem_turma',))
        turmas = self.DATASET['turma'].fillna('sem_turma')

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
        _, amount_parcelas = self.parcelas_split_label_n_amount(parcelas)
        _, amount_producao = self.split_label_n_amount(producao)
        _, amount_multa = self.split_label_n_amount(multa)
        _, amount_desconto = self.split_label_n_amount(desconto)
        _, amount_adesao = self.split_label_n_amount(adesao)

        # fill empty spaces with zeros
        amount_parcelas = [self.fill_empty(value, 0) for value in amount_parcelas]
        amount_producao = [self.fill_empty(value, 0) for value in amount_producao]
        amount_multa = [self.fill_empty(value, 0) for value in amount_multa]
        amount_desconto = [self.fill_empty(value, 0) for value in amount_desconto]
        amount_adesao = [self.fill_empty(value, 0) for value in amount_adesao]

        # Convert numeric strings to number
        amount_parcelas = [self._str_to_float(value) for value in amount_parcelas]
        amount_producao = [self._str_to_float(value) for value in amount_producao]
        amount_multa = [self._str_to_float(value) for value in amount_multa]
        amount_desconto = [self._str_to_float(value) for value in amount_desconto]
        amount_adesao = [self._str_to_float(value) for value in amount_adesao]
  
        
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

    def incomes_table(self, data):
        """ 
        Generate a table with a total sum in the end for each income.
        The total is assigned as values of the dictionary 'col_sum" and it's place is in the 
        last line and below the column indicated by the keys.
        """
        df = pd.DataFrame (data)
        col_sum = {
            'TURMA': None,
            'TITULO': None,
            'VENCIMENTO': None,
            'SACADO': 'TOTAL',
            'VAL_RECEBIDO':sum(df['VAL_RECEBIDO']),
            'VAL_PARCELA': sum(df['VAL_PARCELA']),
            'VAL_PRODUCAO': sum(df['VAL_PRODUCAO']),
            'VAL_MULTA': sum(df['VAL_MULTA']),
            'VAL_DESCONTO': sum(df['VAL_DESCONTO']),
            'VAL_ADESAO': sum(df['VAL_ADESAO']),
            'DATA_CREDITO':None,
        }
        # print(col_sum['VAL_RECEBIDO'])
        return df.append(col_sum, ignore_index=True)

            
        # name_turmas = data['TURMA'].unique()
        # turmas = {}
        # for turma in name_turmas:
        #     turmas[f'turma'] = df[df['TURMA'] == turma]

    
    def comission_table(self, data: dict):
        pass

    # def income_table_format(self, writer,workbook, worksheet):
    #     cell_format = workbook.add_format({'font_color': 'green'})

    #     # cell_format.set_pattern(1)  # This is optional when using a solid fill.
    #     # bg_color = cell_format.set_bg_color('blue')
    #     worksheet.set_row(0,20,cell_format)
    #     writer.close()

    def export_excel(self, df):
        """ Export the treated dataframe to a excel file """
        default_save_names = self.SETTINGS['default_save_name']['incomes_table']
        writer = pd.ExcelWriter(default_save_names['file_name'], engine='xlsxwriter')
        if True:
            df.to_excel(writer, sheet_name=default_save_names['sheet_name'], index=False)
        writer.close()
        # workbook  = writer.book
        # worksheet = writer.sheets['incomes']
        # self.income_table_format(writer,workbook, worksheet)


    def run(self):
        """ Main method to treat and export the data"""
        new_data = pd.DataFrame(data=self.apply_treatment())
        model = self.incomes_table(new_data)
        self.export_excel(model)


if __name__ == '__main__':
    DataEngineer().run()
    # DataEngineer().apply_treatment()
    # DataEngineer()._regex_build()