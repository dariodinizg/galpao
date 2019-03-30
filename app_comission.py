import operator
from csvstats import DataCSV


data = DataCSV('csvrel2.csv')


def string_formating(str_list):
    values = []
    for idx in range(len(str_list)):
        str_list[idx] = str_list[idx].lstrip()
        str_list[idx] = str_list[idx].rstrip()
        values.append(str_list[idx])
    return values


# Import columns data into lists
turma = data.access_column('turma')
titulos = data.access_column('titulos')
sacado = data.access_column('sacado')
credito = data.access_column('credito')
raw_descritivo = data.access_column('descritivo')

# Raw data treatment
turma = string_formating(turma)
sacado = string_formating(sacado)
credito = string_formating(credito)
raw_descritivo = string_formating(raw_descritivo)


# Table lines
def separate_lines(column_str, criteria):
    # Tratando informações do descritivo para separar diferentes classificações.
    values = column_str[:]
    for idx in range(len(values)):
        # Remove espaços desnecessários que geram linhas vazias e separa as classificações de contas
        values[idx] = values[idx].split(criteria)
    return values


descritivo = separate_lines(raw_descritivo, '\n')
# print(descritivo[1])


def classificator_instr(lista_str, match_str):
    # Uso -> Separação dos valores de adesao, multas e produção
    # Para uma lista de dois níveis, busca pela match_str em cada elemento do segundo nível e adiciona a lista
    # 'columns'.
    # Caso não encontre nenhum match para a linha, retorna zero para manter o pareamento com as outras colunas.

    column = []
    for line in lista_str:
        false_checks = []
        my_item = ''
        for element in line:
            if match_str in element.lower():
                my_item = element
            else:
                false_checks.append(0)

            if len(false_checks) == len(line):
                my_item = 0

        column.append(my_item)

    return column


adesao = classificator_instr(descritivo, 'ades')
multas = classificator_instr(descritivo, 'mult')
producao = classificator_instr(descritivo, 'prod')


def classificator_notinstr(lista_str, *match_str):
    # Itera uma lista separando, em outra lista, valores que NÃO cumpre com os critérios fornecidos.

    column = []
    for line in lista_str:
        invalid = []
        for element in line:
            # Primeira iteração: Lista com os valores a serem excluidos
            for search in match_str:
                if search.lower() in element.lower():
                    invalid.append(element)
                else:
                    pass
        for element in line:
            # Segunda iteração: Compara os elementos da lista fonte com aqueles invalidos.
            if element not in invalid:
                column.append(element)
    return column


parcelas = classificator_notinstr(descritivo, 'ade', 'mult', 'prod')


# titulos_descritivo = [[tur,ti,des] for tur,ti,des in zip(turma,titulos, descritivo)]
# print(titulos_descritivo[1])
#
# pagamentos = {}
# for tur, ti, des in titulos_descritivo:
#     pass
