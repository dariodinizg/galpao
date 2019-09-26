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

    def test_fill_values(self):
        """ test for method fill_values """
        col_turmas = self.df['turma']
        col_turmas = col_turmas.apply(self.engineer.fill_values, args=('sem_turma',))
        self.assertEqual(col_turmas[0], 'sem_turma')

    def test_str_normalize(self):
        """ test for method str_normalize """
        descritivo = self.descritivo.apply(self.engineer.str_normalize)
        self.assertEqual(descritivo[0], self.proof['descritivo_normalize'][0])

    def test_strip_n_split(self):
        """ test for method strip_n_split """
        goal = ['parcela de anuidade - 3ª/12             R$ 435,00',
                'Valor de produção - AÉR INI PAL - 3ª/12 R$  16,66']
        descritivo = self.descritivo.apply(self.engineer.strip_n_split)
        self.assertEqual(descritivo[0], goal)

    def setup_descritivo(self):
        """ Normalize and split the values of column 'descritivo' for test cases """
        return self.descritivo.apply(self.engineer.str_normalize).apply(self.engineer.strip_n_split)

    # @skip('teste')
    def test_get_match(self):
        """ test for method get_match """
        treated_descritivo = self.setup_descritivo()
        patterns = self.settings['classification_patterns']
        adesao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['adesao'],))
        producao = treated_descritivo.apply(self.engineer.get_match, args=(patterns['producao'],))
        self.assertEqual(adesao[3], self.proof['adesao'][1])
        self.assertEqual(producao[3], self.proof['producao'][1])

    # def test_matcher_str_n_split(self):
    # Usar descritivo[3]
    #     config_json = {
    #         'adesao':'ades',
    #         'producao':'produ'
    #     }

    #     adesao = 'TX ADESÃO - 1ª/1          R$ 220,00'
    #     producao = 'TAXA PROD - 1ª/10         R$  20,00'
    #     parcela = 'ARTE CIRC  ADOL 1 - 3ª/12 R$ 435,00'
