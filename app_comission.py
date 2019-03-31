import operator
from csvstats import DataCSV
import csv


data = DataCSV('csv_data.csv')


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
venc = data.access_column('vencimento')
raw_descritivo = data.access_column('descritivo')

# Raw data treatment
turma = string_formating(turma)
sacado = string_formating(sacado)
credito = string_formating(credito)
raw_descritivo = string_formating(raw_descritivo)
# print(raw_descritivo[0])


# Table lines
def separate_lines(column_str, criteria):
    # Tratando informações do descritivo para separar diferentes classificações.
    values = column_str[:]
    for idx in range(len(values)):
        # Remove espaços desnecessários que geram linhas vazias e separa as classificações de contas
        values[idx] = values[idx].split(criteria)
    return values


descritivo = separate_lines(raw_descritivo, '\n')
# print(descritivo[0])


def matcher_instr(lista_str, match_str):
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
                my_item = ''

        column.append(my_item)

    return column


def matcher_not_instr(lista_str, *match_str):
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


def values_split(lista_str):
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


adesao = matcher_instr(descritivo, 'ades')
tipo_adesao, valor_adesao = values_split(adesao)

multas = matcher_instr(descritivo, 'mult')
tipo_multa, valor_multa = values_split(multas)

producao = matcher_instr(descritivo, 'prod')
tipo_prod, valor_prod = values_split(producao)

parcelas = matcher_not_instr(descritivo, 'ades', 'multa', 'prod', 'produ')
tipo_parcelas, valor_parcelas = values_split(parcelas)
def negative_values(lista_descr, *lista_vals):
    for idx, item in enumerate(zip(lista_descr, lista_vals)):
        if 'descon' in item[0].lower():
            lista_vals[0][idx] = f'-{lista_vals[0][idx].lstrip()}'
            lista_vals[1][idx] = f'-{lista_vals[1][idx].lstrip()}'

# negative_values(tipo_parcelas, valor_parcelas, valor_prod)


calc_adesao = data.col_str2numbers(valor_adesao)
calc_multa = data.col_str2numbers(valor_multa)
calc_parcelas = data.col_str2numbers(valor_parcelas)
calc_prod = data.col_str2numbers(valor_prod)

def output_comission_table():
    tb_columns = (turma, titulos, venc, sacado, valor_parcelas, valor_prod, valor_multa, valor_adesao)
    mytable = [[tur, tit, ven, sac, parc, prod, mul, ade]
               for tur, tit, ven, sac, parc, prod, mul, ade in zip(*tb_columns)]

    with open('table_incomes.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['turma', 'titulo', 'vencimento', 'sacado', 'parcela mensal', 'taxa_prod', 'multa', 'adesao']
        writer.writerow(header)
        for row in mytable:
            writer.writerow([*row])
        writer.writerow([
            '', '', '', '',
            '{:.2f}'.format(sum(calc_parcelas)).replace('.',','),
            '{:.2f}'.format(sum(calc_prod)).replace('.',','),
            '{:.2f}'.format(sum(calc_multa)).replace('.',','),
            '{:.2f}'.format(sum(calc_adesao)).replace('.',',')])

output_comission_table()

