import operator
from csvstats import DataCSV
import csv


data = DataCSV('source.csv')


def string_formating(str_list):
    values = []
    for idx in range(len(str_list)):
        str_list[idx] = str_list[idx].lstrip()
        str_list[idx] = str_list[idx].rstrip()
        values.append(str_list[idx])
    return values


# Import columns data into lists
turma = data.access_column('turma')
titulos = data.access_column('titulo')
sacado = data.access_column('sacado')
recebido = data.access_column('recebido')
credito = data.access_column('credito')
venc = data.access_column('vencimento')
raw_descritivo = data.access_column('descritivo')

# Raw data treatment
turma = string_formating(turma)
sacado = string_formating(sacado)
credito = string_formating(credito)
raw_descritivo = string_formating(raw_descritivo)

def include_semturma(lista_str):
    for idx, val in enumerate(lista_str):
        if lista_str[idx] == '':
            lista_str[idx] = 'sem turma'

include_semturma(turma)

# Table lines
def separate_lines(column_str, criteria):
    # Tratando informações do descritivo para separar diferentes classificações.
    values = column_str[:]
    for idx in range(len(values)):
        # Remove espaços desnecessários que geram linhas vazias e separa as classificações de contas
        values[idx] = values[idx].split(criteria)
    return values


descritivo = separate_lines(raw_descritivo, '\n')


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
            if match_str.lower() in element.lower():
                my_item = element
            else:
                false_checks.append(0)

            if len(false_checks) == len(line):
                my_item = ''

        column.append(my_item)

    return column


def matcher_not_instr(lista_str, *matches_str):
    # Itera uma lista separando, em outra lista, valores que NÃO cumpre com os critérios fornecidos.

    def search_match(element, matchs):
        invalid = []
        for word in matchs:
            if word.lower() in element.lower():
                invalid.append(element)
        return invalid

    column = []
    for line in lista_str:
        invalidos = []
        for elem in line:
            invalidos = search_match(elem, matches_str)
            if invalidos == []:
                my_elem = elem
                column.append(my_elem)

        if len(line) == len(invalidos):
            column.append('')

            invalidos.clear()

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

parcelas = matcher_not_instr(descritivo, 'ades', 'multa', 'prod', 'desc')
tipo_parcelas, valor_parcelas = values_split(parcelas)


def negative_values(lista_descr, lista_vals):
    for idx, item in enumerate(zip(lista_descr, lista_vals)):
        if 'descon' in item[0].lower():
            lista_vals[idx] = f'-{lista_vals[idx].lstrip()}'

desconto = matcher_instr(descritivo, 'desc')
tipo_desc, valor_desc = values_split(desconto)

negative_values(tipo_desc, valor_desc)

# Conversão em float para realização de cálculos
calc_adesao = data.col_str2numbers(valor_adesao)
calc_multa = data.col_str2numbers(valor_multa)
calc_parcelas = data.col_str2numbers(valor_parcelas)
calc_prod = data.col_str2numbers(valor_prod)
calc_desco = data.col_str2numbers(valor_desc)
calc_receb = data.col_str2numbers(recebido)

def output_income_table():
    tb_columns = (turma, titulos, venc, sacado, recebido, valor_parcelas, valor_prod, valor_multa, valor_desc, valor_adesao)
    mytable = [[turm, titul, venci, sacad, receb, parcel, produ, mult, desc, ades]
               for turm, titul, venci, sacad, receb, parcel, produ, mult, desc, ades in zip(*tb_columns)]
    with open('table_incomes.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['turma', 'titulo', 'vencimento', 'sacado', 'recebido', 'parcela mensal', 'taxa_prod', 'multa', 'desconto', 'adesao']
        writer.writerow(header)
        for row in mytable:
            writer.writerow([*row])

        soma_parcelas = sum(calc_parcelas)
        soma_prod = sum(calc_prod)
        soma_multa = sum(calc_multa)
        soma_desc = sum(calc_desco)
        soma_adesao = sum(calc_adesao)
        total = soma_parcelas + soma_adesao + soma_multa + soma_prod + soma_desc
        writer.writerow(['', '','', 'Total',
        '{:.2f}'.format(total).replace('.',','),
        '{:.2f}'.format(soma_parcelas).replace('.',','),
        '{:.2f}'.format(soma_prod).replace('.',','),
        '{:.2f}'.format(soma_multa).replace('.',','),
        '{:.2f}'.format(soma_desc).replace('.',','),
        '{:.2f}'.format(soma_adesao).replace('.',',')])


output_income_table()


def output_comission_table():
    tb_columns = (turma, titulos, venc, sacado, recebido, valor_parcelas, valor_prod, valor_multa, valor_desc, valor_adesao)
    mytable = [[turm, titul, venci, sacad, receb, parcel, produ, mult, desc, ades]
               for turm, titul, venci, sacad, receb, parcel, produ, mult, desc, ades in zip(*tb_columns)]
    with open('table_comission.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['turma', 'titulo', 'vencimento', 'sacado', 'recebido', 'parcela mensal', 'taxa_prod', 'multa', 'desconto', 'adesao']
        checked_turmas = []
        turma_receb = []
        turma_parc = []
        turma_prod = []
        turma_mult = []
        turma_desc = []
        turma_ades = []
        for row in mytable:
            if row[0] not in checked_turmas:
                checked_turmas.append(row[0])
                writer.writerow(header)

            if row[0] in checked_turmas:
                writer.writerow([*row])

            # turma_receb.append(row[4].replace(',','.'))
            # turma_parc.append(row[5].replace(',','.'))
            # turma_prod.append(row[6].replace(',','.'))
            # turma_mult.append(row[7].replace(',','.'))
            # turma_desc.append(row[8].replace(',','.'))
            # turma_ades.append(row[9].replace(',','.'))
            # print(turma_receb[0])
            #
            # writer.writerow(['', '','', 'Total',
            # '{:.2f}'.format(sum(turma_receb)).replace('.',','),
            # '{:.2f}'.format(sum(turma_parc)).replace('.',','),
            # '{:.2f}'.format(sum(turma_prod)).replace('.',','),
            # '{:.2f}'.format(sum(turma_mult)).replace('.',','),
            # '{:.2f}'.format(sum(turma_desc)).replace('.',','),
            # '{:.2f}'.format(sum(turma_ades)).replace('.',',')])


        # soma_parcelas = sum(calc_parcelas)
        # soma_prod = sum(calc_prod)
        # soma_multa = sum(calc_multa)
        # soma_desc = sum(calc_desco)
        # soma_adesao = sum(calc_adesao)
        # total = soma_parcelas + soma_adesao + soma_multa + soma_prod + soma_desc
        # writer.writerow(['', '','', 'Total',
        # '{:.2f}'.format(total).replace('.',','),
        # '{:.2f}'.format(soma_parcelas).replace('.',','),
        # '{:.2f}'.format(soma_prod).replace('.',','),
        # '{:.2f}'.format(soma_multa).replace('.',','),
        # '{:.2f}'.format(soma_desc).replace('.',','),
        # '{:.2f}'.format(soma_adesao).replace('.',',')])

output_comission_table()
