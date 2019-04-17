from datetime import *
import csv

def include_semturma(lista_str: list):
    for idx, val in enumerate(lista_str):
        if lista_str[idx] == '':
            lista_str[idx] = 'sem turma'


def string_strip(str_list: list) -> list:
    values = []
    for idx in range(len(str_list)):
        str_list[idx] = str_list[idx].strip()
        values.append(str_list[idx])
    return values


def separate_lines(column_str, criteria: str) -> list:
    # Tratando informações do descritivo para separar diferentes classificações.
    values = column_str[:]
    for idx in range(len(values)):
        # Remove espaços desnecessários que geram linhas vazias e separa as classificações de contas
        values[idx] = values[idx].split(criteria)
    return values


def matcher_instr(lista_str: list, match_str: str) -> list:
    # Uso -> Separação dos valores de adesao, multas e produção
    # Para uma lista de dois níveis, busca pela match_str em cada elemento do segundo nível e adiciona a lista
    # 'columns'.
    # Caso não encontre nenhum match para a linha, retorna zero para manter o pareamento com as outras colunas.

    column = []
    for line in lista_str:
        false_checks = []
        my_item = ''
        for element in line:
            if match_str.lower() in element.lower():
                my_item = element
            else:
                false_checks.append(0)

            if len(false_checks) == len(line):
                my_item = ''

        column.append(my_item)

    return column


def values_split(lista_str: list) -> (list, list):
    classification = []
    values = []
    for idx, val in enumerate(lista_str):
        if len(lista_str[idx]) > 0:
            lista_str[idx] = val.split('R$')
            classification.append(lista_str[idx][0].strip())
            values.append(lista_str[idx][1].strip())
        else:
            classification.append('')
            values.append('')
    return classification, values


def matcher_not_instr(lista_str: list):
    # Itera uma lista separando, em outra lista, valores que NÃO cumpre com os critérios fornecidos.
    # 'ades', 'multa', 'prod', 'desc'
    column = []
    for line in lista_str:
        valid_element = None
        for element in line:
            if 'ades' not in element.lower() \
                    and 'prod' not in element.lower() \
                    and 'mult' not in element.lower() \
                    and 'desco' not in element.lower():
                valid_element = element
        if valid_element is None:
            column.append('')
        else:
            column.append(valid_element)

    return column


def output_date():
    # Retorna o dia e o horário em que o programa gerou o output
    now_time = datetime.now().strftime('%d/%m/%Y às %H:%M')

    return f'Emissão do relatório: {now_time}'


def payment_validity(col_dates: list, first_date: str, last_date: str) -> list:
    start_date = datetime.strptime(first_date, '%d/%m/%Y')
    end_date = datetime.strptime(last_date, '%d/%m/%Y')
    validity = []
    for my_date in col_dates:
        date_obj = datetime.strptime(my_date, '%d/%m/%Y')
        if date_obj < start_date:
            validity.append('atrasado')
        elif date_obj > end_date:
            validity.append('antecipado')
        else:
            validity.append('...')
    return validity


def negative_values(lista_descr, lista_vals):
    for idx, item in enumerate(zip(lista_descr, lista_vals)):
        if 'descon' in item[0].lower():
            lista_vals[idx] = f'-{lista_vals[idx].lstrip()}'

