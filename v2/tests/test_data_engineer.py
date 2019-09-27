from data_engineer import DataEngineer
import pandas as pd
from unittest import TestCase, skip
import os
import sys
sys.path.append(os.getcwd())


class TestDataEngineer(TestCase):

    """ 
    Tests for class DataEngineer
    It uses a fixture saved in a excel file, within a sheet named 'proof'
    """

    def setUp(self):
        self.engineer = DataEngineer()
        self.settings = DataEngineer().SETTINGS
        self.df = DataEngineer().DATASET
        self.descritivo = self.df['descritivo']
        self.proof = pd.read_excel('proof_model.xls', sheet_name='proof')

    def test_open_dataset(self):
        """ Verify if the dataset was correctly opened by the DataEngineer class """
        df_header = ('turma', 'titulo', 'vencimento', 'sacado','recebido', 'credito', 'descritivo')
        self.assertEqual(tuple(self.df.head(0)), df_header)

    def test_fill_empty(self):
        """ test for method fill_empty """
        col_turmas = self.df['turma']
        col_turmas = col_turmas.apply(self.engineer.fill_empty, args=('sem_turma',))
        self.assertEqual(col_turmas[0], 'sem_turma')

    def test_str_normalize(self):
        """ test for method str_normalize """
        descritivo = self.descritivo.apply(self.engineer.str_normalize)
        self.assertEqual(descritivo[0], self.proof['descritivo_normalize'][0])

    def test_strip_n_split(self):
        """ test for method strip_n_split """
        goal = ['parcela de anuidade - 3ª/12             R$ 435,00',
                'Valor de produção - AÉR INI PAL - 3ª/12 R$  16,66']
        descritivo = self.descritivo.apply(self.engineer.strip_n_split, args=('\n',))
        self.assertEqual(descritivo[0], goal)

    def setup_descritivo(self):
        """ 
        Normalize and split the values of column 'descritivo' for test cases below.
        ATENTION: Only uses after the tests above returned success.
        """
        return self.descritivo.apply(self.engineer.str_normalize).apply(self.engineer.strip_n_split, args=('\n'))

    # @skip('teste')
    def test_get_match(self):
        """ test for method get_match """
        treated_descritivo = self.setup_descritivo()
        patterns = self.settings['classification_patterns']
        adesao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['adesao'],))
        self.assertEqual(adesao[3], self.proof['adesao'][1])
        # producao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['producao'],))
        # self.assertEqual(producao[3], self.proof['producao'][1])

    def test_get_non_match(self):
        """ Test for get_non_match method. """
        treated_descritivo = self.setup_descritivo()
        parcela = pd.Series(data=DataEngineer().get_non_match(treated_descritivo))
        # parcela = treated_descritivo.apply(self.engineer.get_non_match)
        self.assertEqual(parcela[0], self.proof['parcela'][0])

    def test_split_label_n_amount1(self):
        """ Test for split_label_n_amount method, based in the value for column adesao"""
        treated_descritivo = self.setup_descritivo()
        patterns = self.settings['classification_patterns']
        adesao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['adesao'],))
        test_df = self.engineer.split_label_n_amount(adesao)
        self.assertEqual(test_df[1][3], self.proof['valor_adesao'][1])

    def test_split_label_n_amount2(self):
        """ Test for split_label_n_amount method, based in the information for column adesao"""
        treated_descritivo = self.setup_descritivo()
        patterns = self.settings['classification_patterns']
        adesao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['adesao'],))
        test_df = self.engineer.split_label_n_amount(adesao)
        self.assertEqual(test_df[0][3], self.proof['info_adesao'][1])

    # def test_split_label_n_amount3(self):
    #     """ Test for split_label_n_amount method, based in the value for column parcelas"""
    #     treated_descritivo = self.setup_descritivo()
    #     parcelas = treated_descritivo.apply(self.engineer.get_non_match)
    #     test_df = self.engineer.split_label_n_amount(parcelas)
    #     self.assertEqual(test_df[1][3], '')

    # def test_split_label_n_amount4(self):
    #     """ Test for split_label_n_amount method, based in the information for column parcelas"""
    #     treated_descritivo = self.setup_descritivo()
    #     parcelas = treated_descritivo.apply(self.engineer.get_non_match)
    #     test_df = self.engineer.split_label_n_amount(parcelas)
    #     self.assertEqual(test_df[0][3], '')

    def test_new_dataframe_consistency(self):
        df_model = pd.DataFrame(data=self.engineer.apply_treatment())
        parameter = len(self.df['titulo'])
        columns = list(df_model)
        for column in columns:
            col_size = df_model[f"{column}"].size
            try:
                self.assertEqual(df_model[column].size, parameter)
            except AssertionError:
                print(f'Column {column} dont match the parameter. {col_size} != {parameter}')
        