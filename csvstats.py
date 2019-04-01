import csv
import operator


class DataCSV(object):
    # Modulo para análise de arquivo csv.
    # Para utilizá-lo, crie uma instância filha e passe o nome do arquivo.csv como parametro.

    def __init__(self, csv_file):
        self.filename = csv_file

    def __call_reader__(self):
        class MyDialect:
            delimiter = ';'

        # Função criada para chamar o arquivo.csv antes de cada iteração.
        # O método de abertura escolhido foi o csv.DictReader

        self.csv_file = open(self.filename, 'r')
        self.csv_reader = csv.DictReader(self.csv_file, dialect=MyDialect)
        return self.csv_reader

    def access_column(self, name_col, num_values=None):
        # Acessa uma coluna('name_col') do arquivo e retorna uma lista contendo uma quantidade de
        # valores definida('num_values') para visualização. Por padrão, todos os valores serão incluidos na listagem.

        self.__call_reader__()
        values = []
        for row in self.csv_reader:
            values.append(row[name_col])
        selected_values = values[:num_values]
        return selected_values

    def columns_names(self):
        # Retorna uma lista contendo todos os nomes das colunas do arquivo csv.

        self.__call_reader__()
        col_names = []
        for columns in self.csv_reader:
            for key in columns.keys():
                if (key is not None) and (key != ''):
                    col_names.append(key)
            return col_names

    def print_len_columns(self):

        # Retorna a quantidade de valores em cada lista com dados das colunas arquivo csv.

        for column in self.columns_names():
            print(f'coluna {column} : {len(self.access_column(column))} linhas')

    def pair_values_list(self, name_col1, name_col2):

        # Cria uma lista a partir do pareamento dos valores de duas colunas, indicadas como
        # strings em name_col1 e name_col2.

        self.__call_reader__()
        pairs = list(zip(self.access_column(name_col1), self.access_column(name_col2)))
        return pairs

    def count_values(self, name_col, unique=False):

        # Conta o número de valores existentes em uma coluna indicada em name_col.
        # Para eliminar contagem de valores repetidas defina o parametro 'unique' para True

        source = self.access_column(name_col)
        if unique is True:
            values = set(source)
        else:
            values = source
        return len(values)

    def rank_higher(self, col_criteria, col_elements, num_elements):
        # Retorna uma lista classificatória em ordem descendente dos elementos da coluna (col_elements)
        # a partir dos valores de critério (col_criteria) e número de posições definidos (num_elements).

        source = self.pair_values_list(col_criteria, col_elements)
        ordered_source = sorted(source, reverse=True, key=operator.itemgetter(0))
        ranking = []
        for pair in ordered_source[0:num_elements]:
            ranking.append(pair[1])

        return ranking

    def value_ocurrency(self, name_col):
        # Conta a quantidade de valores repetidos que uma coluna (name_col) possui.

        source = self.access_column(name_col)
        unique_values = set(source)
        values_ocurrency = {}
        for keys in unique_values:
            values_ocurrency[int(keys)] = source.count(keys)
        return values_ocurrency

    def col_str2numbers(self,ref_lista):
        str_lista = ref_lista.copy()
        # Tratamento para uso de funções de calculo. Retorna uma cópia da lista fonte com números em float
        values = []
        for idx,_ in enumerate(str_lista):
            str_lista[idx] = str_lista[idx].strip().replace(',', '.')
            if str_lista[idx] != '':
                str_lista[idx] = float(str_lista[idx])
                values.append(str_lista[idx])
            else:
                values.append(0)
        return values.copy()
