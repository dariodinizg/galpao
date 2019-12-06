import pandas as pd
import json
import re
from decimal import Decimal, ROUND_HALF_DOWN, localcontext, ROUND_DOWN
from StyleFrame import StyleFrame, Styler, utils
from datetime import datetime

from config_manager import ConfigManager


class DataEngineer:

    SETTINGS = ConfigManager('general_config.json').settings
    BUSINESS = ConfigManager('business_config.json').settings
    PATTERNS = SETTINGS['classification_patterns']

    def __init__(self, filename_xls, start_date, end_date):
        self.dataset = pd.read_excel(filename_xls)
        self.start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
        self.end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        self.comission_date = f"{self.start_date.strftime('%d/%m/%Y')} a {self.end_date.strftime('%d/%m/%Y')}"

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
        """ Change empty values to new_value """
        if str(current_value) == 'nan':
            return new_value
        return current_value

    @staticmethod
    def str_upper(row):
        return row.upper()
    
    @staticmethod
    def strip_n_split(row, separator):
        """Remove white spaces and split new lines, forming a list."""
        return row.strip().split(separator)

    @staticmethod
    def add_negative_sign(row):
        return row * -1

    def get_match(self, pd_serie, pattern):
        """ 
        Select a value from a list that correspond to a given value, or
        returns empty if no match was found.
        PS: Assign the result to a new variable. Dont override the original
         """
         
        regex = re.compile(f"({pattern})")
        valids = []
        for row in pd_serie:
            invalid = []
            row_valid = []
            for value in row:
                if bool(regex.search(value)):
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
                treated_valid.append(1)
                
        return treated_valid

    def get_non_match(self, pd_serie):
        """Select a value from a list that do not correspond a given regex"""
        regex = re.compile(self._regex_build())
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

    def to_datetime(self, pd_serie):
        pd_serie = pd.to_datetime(pd_serie ,format=r"%d/%m/%Y",dayfirst=True, utc=False)
        return pd_serie

    def split_label_n_amount(self, list_obj: list):
        """ 
        Split the payment's label and its amount in two columns.
        It needs a different function for split label and amount since the 
        parameter is not a panda.Series, but a python list.
        """
        label_list = []
        amount_list = []
        for value in list_obj:
            if type(value) != int:
                try:
                    label,amount = value.split('R$')
                    label_list.append(label)
                    amount_list.append(amount.strip())
                except AttributeError:
                    continue
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
        turmas = self.dataset['turma'].fillna('sem_turma')

        # Normalize descritivo column and split each line row string in a list of values.
        descritivo = self.dataset['descritivo'].apply(self.str_upper)
        descritivo = descritivo.apply(self.strip_n_split, args=('\n',))

        # Select values of a panda.Series that dont match a criteria.
        parcelas = pd.Series(data=self.get_non_match(descritivo))
        
        # Select values of a panda.Series that match a criteria.
        adesao = self.get_match(descritivo, self.PATTERNS['adesao'])
        adesao = self.get_match(descritivo, self.PATTERNS['adesao'])
        producao = self.get_match(descritivo, self.PATTERNS['producao'])
        multa = self.get_match(descritivo, self.PATTERNS['multa'])
        desconto = self.get_match(descritivo, self.PATTERNS['desconto'])

        # Split label and amount
        _, amount_parcelas = self.split_label_n_amount(parcelas)
        _, amount_producao = self.split_label_n_amount(producao)
        _, amount_multa = self.split_label_n_amount(multa)
        _, amount_desconto = self.split_label_n_amount(desconto)
        _, amount_adesao = self.split_label_n_amount(adesao)

        amount_parcelas = pd.Series(data=amount_parcelas).apply(self.fill_empty, args=(0,))
        amount_producao = pd.Series(data=amount_producao).apply(self.fill_empty, args=(0,))
        amount_multa    = pd.Series(data=amount_multa).apply(self.fill_empty, args=(0,))
        amount_adesao   = pd.Series(data=amount_adesao).apply(self.fill_empty, args=(0,))
        amount_desconto = pd.Series(data=amount_desconto).apply(self.fill_empty, args=(0,))

        # Convert numeric strings to number
        amount_parcelas = amount_parcelas.apply(self._str_to_float)
        amount_producao = amount_producao.apply(self._str_to_float)
        amount_multa    = amount_multa.apply(self._str_to_float)
        amount_desconto = amount_desconto.apply(self._str_to_float)
        amount_adesao   = amount_adesao.apply(self._str_to_float)

        # Add negative sign to amount_desconto
        amount_desconto = amount_desconto.apply(self.add_negative_sign)

        """ 
        Convert the date columns to datetime elements and change credito column to string
        in order for the excel to correct display it
        """
        vencimento = self.to_datetime(self.dataset['vencimento'])
        credito = self.to_datetime(self.dataset['credito']).apply(lambda date_string: f"{date_string.date().strftime('%d/%m/%Y')}")
       
        treated_df = {
            'TURMA': turmas,
            'TITULO': self.dataset['titulo'],
            'VENCIMENTO': vencimento,
            'SACADO': self.dataset['sacado'],
            'VAL_RECEBIDO':self.dataset['recebido'],
            'VAL_PARCELA': amount_parcelas,
            'VAL_PRODUCAO': amount_producao,
            'VAL_MULTA': amount_multa,
            'VAL_DESCONTO': amount_desconto,
            'VAL_ADESAO': amount_adesao,
            'DATA_CREDITO': credito,
        }
        pd.DataFrame(treated_df)
        col_multas_comission = pd.Series(data=self.comission_multas(treated_df))
        treated_df['comission_multas'] = col_multas_comission
        return treated_df

    def comission_multas(self, df):
        fator_multa = self.BUSINESS['fator_multa']
        values = []
        for parcela, vencimento in zip(df['VAL_PARCELA'], df['VENCIMENTO']):
            if bool(parcela) and vencimento < self.start_date:
                values.append(Decimal(parcela * fator_multa).quantize(Decimal('0.00')))
            else:
                values.append(0)
        return values

    def comission_table(self, df):
        sort_criteria = self.SETTINGS['sort_data']['incomes_table']
        df = df.sort_values(by=['TURMA', sort_criteria])
        header_dict = {
                'TURMA':['TURMA'] ,
                'TITULO': ['TITULO'],
                'VENCIMENTO': ['VENCIMENTO'],
                'SACADO': ['SACADO'],
                'VAL_RECEBIDO':['VAL_RECEBIDO'],
                'VAL_PARCELA': ['VAL_PARCELA'],
                'VAL_PRODUCAO': ['VAL_PRODUCAO'],
                'VAL_MULTA': ['VAL_MULTA'],
                'VAL_DESCONTO': ['VAL_DESCONTO'],
                'VAL_ADESAO': ['VAL_ADESAO'],
                'DATA_CREDITO':['DATA_CREDITO'],
                'comission_multas':['comission_multas']
            }
        header_df = pd.DataFrame(data=header_dict)
        schema_df = {
                'TURMA':[] ,
                'TITULO': [],
                'VENCIMENTO': [],
                'SACADO': [],
                'VAL_RECEBIDO':[],
                'VAL_PARCELA': [],
                'VAL_PRODUCAO': [],
                'VAL_MULTA': [],
                'VAL_DESCONTO': [],
                'VAL_ADESAO': [],
                'DATA_CREDITO':[],
                'comission_multas':[]
            }
        model_df = pd.DataFrame(data=schema_df)
        
        TWO_PLACES = Decimal('0.00')
        for turma in df['TURMA'].unique():
            turma_df = df[df['TURMA'] == turma]
            sum_recebido  =  Decimal(sum(turma_df['VAL_RECEBIDO'])).quantize(TWO_PLACES)
            sum_parcela   =  Decimal(sum(turma_df['VAL_PARCELA'])).quantize(TWO_PLACES)
            sum_producao  =  Decimal(sum(turma_df['VAL_PRODUCAO'])).quantize(TWO_PLACES)
            sum_multa     =  Decimal(sum(turma_df['VAL_MULTA'])).quantize(TWO_PLACES)
            sum_descontos =  Decimal(sum(turma_df['VAL_DESCONTO'])).quantize(TWO_PLACES)
            sum_adesao    =  Decimal(sum(turma_df['VAL_ADESAO'])).quantize(TWO_PLACES)
            sum_comission_multas = Decimal(sum(turma_df['comission_multas'])).quantize(TWO_PLACES)
            with localcontext() as ctx:
                ctx.rounding = ROUND_HALF_DOWN
                col_sum = {
                    'SACADO': 'TOTAL',
                    'VAL_RECEBIDO': self._str_to_float(sum_recebido),
                    'VAL_PARCELA': self._str_to_float(sum_parcela),
                    'VAL_PRODUCAO': self._str_to_float(sum_producao),
                    'VAL_MULTA': self._str_to_float(sum_multa),
                    'VAL_DESCONTO': self._str_to_float(sum_descontos),
                    'VAL_ADESAO': self._str_to_float(sum_adesao),
                }
            turma_df = turma_df.append(col_sum, ignore_index=True)
            model_df = model_df.append(turma_df, ignore_index=True)
            date_line = {
                    'TURMA': f"Periodo: {self.comission_date}",
                    'TITULO': "R$"
            }
            model_df = model_df.append(date_line, ignore_index=True)

            if turma in self.BUSINESS['TURMAS'] and len(self.BUSINESS['TURMAS'][turma].keys()) > 0:
                with localcontext() as ctx:
                    ctx.rounding = ROUND_HALF_DOWN
                    for partner in self.BUSINESS['TURMAS'][turma].keys():
                        comission_factor = Decimal(self.BUSINESS['TURMAS'][turma][partner])
                        comission_line = {
                            'TURMA': partner,
                            'TITULO':self._str_to_float(((sum_parcela + sum_comission_multas)* Decimal(comission_factor)).quantize(TWO_PLACES)),
                        }
                        model_df = model_df.append(comission_line, ignore_index=True)
            model_df = model_df.append(pd.Series(), ignore_index=True)
            model_df = model_df.append(header_df, ignore_index=True)
        model_df.drop('comission_multas', axis=1, inplace=True)
        model_df.drop(index=(len(model_df)-1), inplace=True)
        return model_df

    def incomes_table(self, df):
        """ 
        Generate a table with a total sum in the end for each income.
        The total is assigned as values of the dictionary 'col_sum" and it's place is in the 
        last line and below the column indicated by the keys.
        """
        sort_criteria = self.SETTINGS['sort_data']['incomes_table']
        model_df = df.sort_values(by=['TURMA', sort_criteria])
        TWO_PLACES = Decimal('0.00')
        sum_recebido  =  Decimal(sum(model_df['VAL_RECEBIDO'])).quantize(TWO_PLACES)
        sum_parcela   =  Decimal(sum(model_df['VAL_PARCELA'])).quantize(TWO_PLACES)
        sum_producao  =  Decimal(sum(model_df['VAL_PRODUCAO'])).quantize(TWO_PLACES)
        sum_multa     =  Decimal(sum(model_df['VAL_MULTA'])).quantize(TWO_PLACES)
        sum_descontos =  Decimal(sum(model_df['VAL_DESCONTO'])).quantize(TWO_PLACES)
        sum_adesao    =  Decimal(sum(model_df['VAL_ADESAO'])).quantize(TWO_PLACES)
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_DOWN
            col_sum = {
                    'SACADO': 'TOTAL',
                    'VAL_RECEBIDO': self._str_to_float(sum_recebido),
                    'VAL_PARCELA': self._str_to_float(sum_parcela),
                    'VAL_PRODUCAO': self._str_to_float(sum_producao),
                    'VAL_MULTA': self._str_to_float(sum_multa),
                    'VAL_DESCONTO': self._str_to_float(sum_descontos),
                    'VAL_ADESAO': self._str_to_float(sum_adesao),
                }
            model_df = model_df.append(col_sum, ignore_index=True)
            date_line = {
                    'SACADO': f"Periodo: {self.comission_date}"
            }
            model_df = model_df.append(date_line, ignore_index=True)
        return model_df

    def _format_table(self, df):
        sort_criteria = self.SETTINGS['sort_data']['incomes_table']
        excel_format = df[sort_criteria].apply(
            lambda value: f"{value.date().strftime(r'%d/%m/%Y')}" 
            if f"{type(value)}" == "<class 'pandas._libs.tslibs.timestamps.Timestamp'>"
            else value)
        df[sort_criteria] = excel_format
        
        sf = StyleFrame(df)
        sf.apply_style_by_indexes(indexes_to_style=sf[sf['TITULO'] != ''],styler_obj=Styler(font_size=10))
        sf.apply_style_by_indexes(indexes_to_style=sf[sf['TURMA'] == 'TURMA'],styler_obj=Styler(bold=False,
                                                bg_color=utils.colors.grey,
                                                border_type=utils.borders.thin,
                                                font_size=10,
                                                wrap_text=False,
                                                shrink_to_fit=False))
        sf.apply_style_by_indexes(indexes_to_style=sf[sf['SACADO'] == 'TOTAL'],styler_obj=Styler(font_size=10, bold=True))
        sf.apply_headers_style(styler_obj=Styler(bold=False,
                                                bg_color=utils.colors.grey,
                                                border_type=utils.borders.thin,
                                                font_size=10,
                                                wrap_text=False,
                                                shrink_to_fit=False))
        col_width = {
            'TURMA': 32,
            'TITULO': 8,
            'VENCIMENTO': 12,
            'SACADO': 34,
            'VAL_RECEBIDO':13.2,
            'VAL_PARCELA': 12,
            'VAL_PRODUCAO': 12,
            'VAL_MULTA': 12,
            'VAL_DESCONTO': 12,
            'VAL_ADESAO': 12,
            'DATA_CREDITO':12,
        }
        sf.set_column_width_dict(col_width)
        return sf

    def _export_excel(self, df, filename):
        """ Export the treated dataframe to a excel file """
        #+ default_save_names = self.SETTINGS['default_save_name']['incomes_table']
        styled_table = self._format_table(df)
        styled_table.to_excel(filename).save()
        
    def run(self, export_comission=False, export_incomes=False):
        """ Main method to treat and export the data"""
        new_data = pd.DataFrame(data=self.apply_treatment())
        if export_incomes is True:
            income_table = self.incomes_table(new_data)
            self._export_excel(income_table, 'incomes.xls')
        if export_comission is True:
            comission_table = self.comission_table(new_data)
            self._export_excel(comission_table, 'comissions.xls')


# if __name__ == "__main__":
    # DataEngineer('comission_abril.XLS', "01/01/2019", "30/01/2019").run(export_comission=True, export_incomes=False)
    # DataEngineer('comission_abril.XLS', "01/01/2019", "30/01/2019").apply_treatment()
    