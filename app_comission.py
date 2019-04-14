from csvstats import DataCSV
import csv
from datetime import *


def include_semturma(lista_str: list):
    for idx, val in enumerate(lista_str):
        if lista_str[idx] == '':
            lista_str[idx] = 'sem turma'


def string_strip(str_list: list) -> list:
    values = []
    for idx in range(len(str_list)):
        str_list[idx] = str_list[idx].lstrip()
        str_list[idx] = str_list[idx].rstrip()
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


def check_valid(element, matchs: str) -> int:
    for match in matchs:
        if match.lower() in element.lower():
            return 0
        else:
            return 1


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
    # Retorna P - passado, V - vigente e F - futuro.
    validity = []
    start_date = datetime.strptime(first_date, '%d/%m/%Y')
    end_date = datetime.strptime(last_date, '%d/%m/%Y')

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


def output_income_table():
    # Exporta uma tabela com todas as informações classificadas em colunas separadas e um total na ultima linha

    tb_columns = (turma, titulos, venc, sacado, val_pgtos, recebido, valor_parcelas,
                  valor_prod, valor_multa, valor_desc, valor_adesao, credito)
    mytable = [[turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred]
               for turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred
               in zip(*tb_columns)]
    with open('table_incomes.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['TURMA', 'TITULO', 'VENCIMENTO', 'SACADO', 'VIGENCIA_DO_PGTO','VAL_RECEBIDO', 'VAL_PARCELA',
                  'VAL_PRODUCAO', 'VAL_MULTA', 'VAL_DESCONTO', 'VAL_ADESAO', 'DATA_CREDITO']
        writer.writerow([f'Periodo de comissão: {data_inicial} a {data_final}'])
        writer.writerow(header)
        for row in mytable:
            writer.writerow([*row])

        soma_parcelas = sum(calc_parcelas)
        soma_prod = sum(calc_prod)
        soma_multa = sum(calc_multa)
        soma_desc = sum(calc_desco)
        soma_adesao = sum(calc_adesao)
        val_comissao = soma_parcelas + soma_desc

        total = soma_parcelas + soma_adesao + soma_multa + soma_prod + soma_desc
        writer.writerow(['', '', '','', 'TOTAL PREVISTO',
                         '{:.2f}'.format(total).replace('.', ','),
                         '{:.2f}'.format(val_comissao).replace('.', ','),
                         '{:.2f}'.format(soma_prod).replace('.', ','),
                         '{:.2f}'.format(soma_multa).replace('.', ','),
                         '{:.2f}'.format(soma_desc).replace('.', ','),
                         '{:.2f}'.format(soma_adesao).replace('.', ',')])
        writer.writerow(['', '', '','', 'TOTAL REALIZADO (- descontos)',
                         '{:.2f}'.format(total).replace('.', ','),
                         '{:.2f}'.format(val_comissao + soma_desc).replace('.', ',')])
        writer.writerow([output_date()])


def output_comission_table():
    # Exporta uma tabela com os valores separados por turma para uso no comissionamento dos valores

    tb_columns = (turma, titulos, venc, sacado, val_pgtos, recebido, valor_parcelas,
                  valor_prod, valor_multa, valor_desc, valor_adesao, credito)
    mytable = [[turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred]
               for turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred
               in zip(*tb_columns)]
    with open('table_comission.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['TURMA', 'TITULO', 'VENCIMENTO', 'SACADO', 'VIGENCIA_DO_PGTO','VAL_RECEBIDO', 'VAL_PARCELA',
                  'VAL_PRODUCAO', 'VAL_MULTA', 'VAL_DESCONTO', 'VAL_ADESAO', 'DATA_CREDITO']

        checked_turmas = []
        # Listas para armazenar valores por turma
        turma_receb = 0.0
        turma_parc = 0.0
        turma_prod = 0.0
        turma_mult = 0.0
        turma_desc = 0.0
        turma_ades = 0.0
        subtotal_previsto = None
        subtotal_realizado = None

        idx = 0

        for row in mytable:  # Divisão de turmas
            if row[0] not in checked_turmas:
                checked_turmas.append(row[0])
                if turma_receb != 0.0:
                    writer.writerow(subtotal_previsto)
                    writer.writerow(subtotal_realizado)
                    turma_receb = 0.0
                    turma_parc = 0.0
                    turma_prod = 0.0
                    turma_mult = 0.0
                    turma_desc = 0.0
                    turma_ades = 0.0
                    writer.writerow('')
                writer.writerow([f'Periodo de comissão: {data_inicial} a {data_final}'])
                writer.writerow(header)

            # Linhas de cada turma

            if row[0] in checked_turmas:
                writer.writerow([*row])

            # Colunas para cálculo por turma
            turma_receb += calc_receb[idx]
            turma_parc += calc_parcelas[idx]
            turma_prod += calc_prod[idx]
            turma_mult += calc_multa[idx]
            turma_desc += calc_desco[idx]
            turma_ades += calc_adesao[idx]

            subtotal_previsto = ['', '','', '', 'SUBTOTAL PREVISTO',
                                 '{:.2f}'.format(turma_receb).replace('.', ','),
                                 '{:.2f}'.format(turma_parc).replace('.', ','),
                                 '{:.2f}'.format(turma_prod).replace('.', ','),
                                 '{:.2f}'.format(turma_mult).replace('.', ','),
                                 '{:.2f}'.format(turma_desc).replace('.', ','),
                                 '{:.2f}'.format(turma_ades).replace('.', ',')]

            subtotal_realizado = ['','', '', '', 'VALOR PARA COMISSAO', '',
                                  '{:.2f}'.format(turma_parc + turma_desc).replace('.', ',')]

            idx += 1

        soma_parcelas = sum(calc_parcelas)
        soma_prod = sum(calc_prod)
        soma_multa = sum(calc_multa)
        soma_desc = sum(calc_desco)
        soma_adesao = sum(calc_adesao)
        total = soma_parcelas + soma_adesao + soma_multa + soma_prod + soma_desc
        writer.writerow(['', '', '', 'TOTAL',
                         '{:.2f}'.format(total).replace('.', ','),
                         '{:.2f}'.format(soma_parcelas).replace('.', ','),
                         '{:.2f}'.format(soma_prod).replace('.', ','),
                         '{:.2f}'.format(soma_multa).replace('.', ','),
                         '{:.2f}'.format(soma_desc).replace('.', ','),
                         '{:.2f}'.format(soma_adesao).replace('.', ',')])
        writer.writerow([output_date()])


# filename = input("\033[36m"'Insira o nome e extensão do arquivo csv que deseja abrir: ')
# start_date = input("\033[36m""Insira a data de inicio do filtro de comissionamento, ano/mês/dia - AAAA/MM/DD: ")
# end_date = input("\033[36m""Insira a data de fim do filtro de comissionamento, ano/mês/dia - AAAA/MM/DD: ")
# data = DataCSV(filename)
data = DataCSV('source.csv')


# Import columns data into lists
turma = data.access_column('turma')
titulos = data.access_column('titulo')
sacado = data.access_column('sacado')
recebido = data.access_column('recebido')
credito = data.access_column('credito')
venc = data.access_column('vencimento')
raw_descritivo = data.access_column('descritivo')

# TRATAMENTO DE INFORMAÇÕES

# Redução de espaços excedentes
turma = string_strip(turma)
include_semturma(turma)
sacado = string_strip(sacado)
credito = string_strip(credito)
raw_descritivo = string_strip(raw_descritivo)

# Separação de linhas em elementos de uma lista
descritivo = separate_lines(raw_descritivo, '\n')

# Separação dos elementos da lista descritivo em colunas únicas
parcelas = matcher_not_instr(descritivo)
adesao = matcher_instr(descritivo, 'ades')
multas = matcher_instr(descritivo, 'mult')
producao = matcher_instr(descritivo, 'prod')
desconto = matcher_instr(descritivo, 'desc')

# Separação entre identificação da conta e o valor da conta
tipo_adesao, valor_adesao = values_split(adesao)
tipo_parcelas, valor_parcelas = values_split(parcelas)
tipo_multa, valor_multa = values_split(multas)
tipo_prod, valor_prod = values_split(producao)
tipo_desc, valor_desc = values_split(desconto)

# Inclusão de sinal negativo para identificação "desconto"
negative_values(tipo_desc, valor_desc)

# Conversão em float para realização de cálculos
calc_adesao = data.col_str2numbers(valor_adesao)
calc_multa = data.col_str2numbers(valor_multa)
calc_parcelas = data.col_str2numbers(valor_parcelas)
calc_prod = data.col_str2numbers(valor_prod)
calc_desco = data.col_str2numbers(valor_desc)
calc_receb = data.col_str2numbers(recebido)

# Classificação de validade dos pagamentos
data_inicial = '28/02/2019'
data_final = '28/03/2019'
val_pgtos = payment_validity(venc, data_inicial, data_final)

output_income_table()
output_comission_table()
