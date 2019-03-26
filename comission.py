from csvstats import DataCSV
import csv
from datetime import datetime


def classificar_receitas(descritivo):
    # Separa cada tipo de conta em uma lista específica
    arte_cir = []
    tx_prod = []
    for elements in descritivo:
        for income_types in elements:
            if 'ARTE CIRC' in income_types:
                arte_cir.append(income_types)
            elif 'TAXA PROD' in income_types:
                tx_prod.append(income_types)
    return arte_cir, tx_prod


def fill_missing_fields(reference_field, *fields):
    # VERIFICAÇÃO DE ENTRADA - Caso dê IndexError, ele retorna um valor personalizável.
    # ['turma', 'sacado', 'parcela mensal', 'valor(R$)', 'data_credito'])

    values = []
    for idx in range(0,len(reference_field)):
        try:
            a = fields[idx][0]
        except:
            a = '0'
        try:
            b = fields[idx][1]
        except:
            b = '0'
        try:
            c = fields[idx][2]
        except:
            c = '0'
        try:
            d = fields[3][idx][1]
        except:
            d = '0'
        try:
            e = fields[4][idx][0]
        except:
            e = '0'
        try:
            f = fields[5][idx][1]
        except:
            f = '0'
        try:
            g = fields[6][idx]
        except:
            g = '0'
        values.append([a,b,c,d,e,f,g])

    return values


def isolar_valores(descritivo):
    # Separa a descrição da receita de seu valor correspondente, usando "R$" como delimitador.

    values = []
    for str in descritivo:
        values.append(str.split('R$'))
    return values


def matcher_instring(lista, lower_str):
    # Look for a string in a list of strings and return a list with the values found.
    # If no match was found, returns a ' ' to fill the place and keep the pairing with other columns

    falses_check = []
    my_item = None
    for element in lista:
        if lower_str in element.lower():
            my_item =  element
        else:
            falses_check.append(element)

    if len(falses_check) == len(lista):
        return ''
    else:
        return my_item


def matcher_notstring(lista, lower_str):
    # Look for a string in a list of strings and return a list with the values found.
    # If no match was found, returns a ' ' to fill the place and keep the pairing with other columns

    falses_check = []
    my_item = None
    for element in lista:
        if lower_str not in element.lower():
            my_item =  element
        else:
            falses_check.append(element)

    if len(falses_check) == len(lista):
        return ''
    else:
        return my_item


def select_income_type_by_str(matcher, source, str_pattern, split_criteria):
    # Uses matcher_instring to form a list of selected values and treat the values, separating the
    # income description of the its value in 'R$'

    selected_values = []
    for element in source:
        selected_values.append(matcher(element,str_pattern))
    for idx in range(len(selected_values)):
        selected_values[idx] = selected_values[idx].split(split_criteria)

    return selected_values


data = DataCSV('csvrel2.csv')  # ['sacado'[idx][0], 'credito', 'turma', 'descritivo']

# importa colunas
turmas = data.access_column('turma')
sacado = data.access_column('sacado')
credito = data.access_column('credito')
descritivo = data.access_column("descritivo")

# Tratando informações do descritivo para separar diferentes classificações.
for idx in range(0, len(sacado)):
    # Remove espaços desnecessários que geram linhas vazias e separa as classificações de contas
    descritivo[idx] = descritivo[idx].rstrip().split('\n')

# Construção de lista com valores que incluam as strings indicadas na função
# e split dos valores da lista usando "R$" como critério
taxa_prod = select_income_type_by_str(matcher_instring, descritivo, 'prod', 'R$')
adesao = select_income_type_by_str(matcher_instring, descritivo, 'ades', 'R$')

my_list = []
for item in descritivo:
    my_list.append(matcher_notstring(item, 'prod'))

# Guarda todas as parcelas em uma mesma lista
parcelas = []
for element in my_list:
    # reconstrói a coluna de parcelas removendo as adesões
    if 'ades' in element.lower():
        parcelas.append('')
    else:
        parcelas.append(element.rstrip())

# Separação de valores de parcela sua classificação usando 'R$' como splitter
for idx in range(len(parcelas)):
    parcelas[idx] = parcelas[idx].split('R$')
    for idx2 in range(len(parcelas[idx])):
        parcelas[idx][idx2] = parcelas[idx][idx2].rstrip()

# Constrói uma lista para classificação e outra para valores
descr_parcelas = []
valor_parcelas = []
for idx3 in range(len(parcelas)):
    descr_parcelas.append(parcelas[idx3][0])
    try:
        valor_parcelas.append(parcelas[idx3][1])
    except IndexError:
        valor_parcelas.append('')

descr_adesao = []
valor_adesao = []
def adesao_organizer():
    global descr_adesao, valor_adesao
    for idx4 in range(len(adesao)):
        descr_adesao.append(adesao[idx4][0])
        try:
            valor_adesao.append(adesao[idx4][1])
        except IndexError:
            valor_adesao.append('')
adesao_organizer()

descr_prod = []
valor_prod = []
def tx_prod_organizer():
    global descr_prod, valor_prod
    for idx in range(len(taxa_prod)):
        descr_prod.append(taxa_prod[idx][0])
        try:
            valor_prod.append(taxa_prod[idx][1])
        except IndexError:
            valor_prod.append('')
tx_prod_organizer()

# Tratamento de colunas literais
def include_semturma(str_lista):
    values = str_lista
    for idx in range(len(values)):
        if values[idx] == '':
            values[idx] = 'sem turma'
    return values
turmas = include_semturma(turmas)

# Tratamento de colunas numéricas
def negative_values():
    global descr_parcelas
    for idx4 in range(len(descr_parcelas)):
        # Inclusão de sinal negativo em itens com desconto
        if 'descon' in descr_parcelas[idx4].lower():
            valor_parcelas[idx4] = f'-{valor_parcelas[idx4].lstrip()}'
negative_values()

def col_str2numbers(str_lista):
    # Tratamento para uso de funções de calculo
    values = str_lista[:]
    for idx in range(len(values)):
        if values[idx] != '':
            values[idx] = values[idx].strip()
            values[idx] = values[idx].replace(',','.')
            values[idx] = float(values[idx])
        else:
            continue
    return values
calc_parcelas = col_str2numbers(valor_parcelas)
calc_prod = col_str2numbers(valor_prod)
calc_adesao = col_str2numbers(valor_adesao)

def col_num2string(str_list, num_list):
    values = str_list
    for idx in range(len(values)):
        if values[idx] != '':
            values[idx] = ('{:.2f}').format(num_list[idx])
            values[idx] = values[idx].replace('.',',')
        else:
            continue
    return values
valor_parcelas = col_num2string(valor_parcelas, calc_parcelas)

# Classificação para atrasados
def check_dates():
    global valor_parcelas

    parc_atrasadas = []
    initial_date = '28/02'
    initial_date = datetime.strptime(initial_date, '%d/%m')

    data_credito = credito[:]
    for idx in range(len(data_credito)):
        data_credito[idx] = data_credito[idx].split('/')
        data_credito[idx] = datetime.strptime(f'{data_credito[idx][0]}/{data_credito[idx][1]}', '%d/%m')

    for idx in range(len(data_credito)):
        if data_credito[idx] < initial_date:
            parc_atrasadas.append(valor_parcelas[idx])
            valor_parcelas[idx] = ''
        else:
            parc_atrasadas.append('')
    return parc_atrasadas
val_vencidos = check_dates()


# # Preparação de dados para escrita
comission_tablerows = []
#list(zip([turmas, sacado,parcelas[0], parcelas[1], credito]))
for idx in range(len(sacado)):
    if len(descr_parcelas[idx]) > 0:
        comission_tablerows.append([turmas[idx], sacado[idx], descr_parcelas[idx], val_vencidos[idx], valor_parcelas[idx], descr_prod[idx], valor_prod[idx], credito[idx]])
    else:
        continue

with open('comission_output.csv', 'w') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    checked_turmas = []
    row_numbers = 0
    for row in comission_tablerows:
        if len(checked_turmas) == 0:
            checked_turmas.append(row[0])
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row_numbers])
            row_numbers += 1
        elif row[0] not in checked_turmas:
            checked_turmas.append(row[0])
            writer.writerow('')
            writer.writerow(['turma', 'sacado', 'classificação parcela', 'valor vencido(R$)', 'valor vigente(R$)', 'class_produção', 'valor prod','data_credito', 'line'])
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row_numbers])
            row_numbers += 1
        else:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row_numbers])
            row_numbers += 1
