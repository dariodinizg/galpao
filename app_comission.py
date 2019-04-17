from csvstats import DataCSV
import csv
import reader as rd
from tkinter import *
from tkinter import filedialog
from os import getcwd



def output_income_table(start_date, end_date):
    my_table_columns, my_calc_columns = data_modeling()

    calc_parcelas = my_calc_columns['parcelas']
    calc_prod = my_calc_columns['producao']
    calc_multa = my_calc_columns['multas']
    calc_desco = my_calc_columns['descontos']
    calc_adesao = my_calc_columns['adesao']

    mytable = [[turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred]
               for turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred
               in zip(*my_table_columns)]
    with open('table_incomes.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['TURMA', 'TITULO', 'VENCIMENTO', 'SACADO', 'VIGENCIA_DO_PGTO','VAL_RECEBIDO', 'VAL_PARCELA',
                    'VAL_PRODUCAO', 'VAL_MULTA', 'VAL_DESCONTO', 'VAL_ADESAO', 'DATA_CREDITO']
        writer.writerow([f'Periodo de comissão: {start_date} a {end_date}'])
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
        writer.writerow([rd.output_date()])


def output_comission_table(start_date, end_date):
    # Exporta uma tabela com os valores separados por turma para uso no comissionamento dos valores

    my_table_columns, my_calc_columns = data_modeling()

    calc_receb = my_calc_columns['recebidos']
    calc_parcelas = my_calc_columns['parcelas']
    calc_prod = my_calc_columns['producao']
    calc_multa = my_calc_columns['multas']
    calc_desco = my_calc_columns['descontos']
    calc_adesao = my_calc_columns['adesao']

    mytable = [[turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred]
                for turm, titul, venci, sacad, val_pgto, receb, parcel, produ, mult, desc, ades, cred
                in zip(*my_table_columns)]

    with open('table_comission.csv', 'w') as exported_table:
        writer = csv.writer(exported_table, delimiter=';')
        header = ['TURMA', 'TITULO', 'VENCIMENTO', 'SACADO', 'VIGENCIA_DO_PGTO','VAL_RECEBIDO', 'VAL_PARCELA',
                    'VAL_PRODUCAO', 'VAL_MULTA', 'VAL_DESCONTO', 'VAL_ADESAO', 'DATA_CREDITO']

        checked_turmas = []

        # Listas para armazenar valores por turma
        turma_recebidos = 0.0
        turma_parcelas = 0.0
        turma_producao = 0.0
        turma_multas = 0.0
        turma_descontos = 0.0
        turma_adesoes = 0.0
        subtotal_previsto = None
        subtotal_realizado = None
        index = 0

        for row in mytable:  # Divisão de turmas
            if row[0] not in checked_turmas:
                checked_turmas.append(row[0])
                if turma_recebidos != 0.0:
                    writer.writerow(subtotal_previsto)
                    writer.writerow(subtotal_realizado)
                    turma_recebidos = 0.0
                    turma_parcelas = 0.0
                    turma_producao = 0.0
                    turma_multas = 0.0
                    turma_descontos = 0.0
                    turma_adesoes = 0.0
                    writer.writerow('')
                writer.writerow([f'Periodo de comissão: {start_date} a {end_date}'])
                writer.writerow(header)

            # Linhas de cada turma

            if row[0] in checked_turmas:
                writer.writerow([*row])

            # Colunas para cálculo por turma
            turma_recebidos += calc_receb[index]
            turma_parcelas += calc_parcelas[index]
            turma_producao += calc_prod[index]
            turma_multas += calc_multa[index]
            turma_descontos += calc_desco[index]
            turma_adesoes += calc_adesao[index]
            subtotal_previsto = ['', '','', '', 'SUBTOTAL PREVISTO',
                                    '{:.2f}'.format(turma_recebidos).replace('.', ','),
                                    '{:.2f}'.format(turma_parcelas).replace('.', ','),
                                    '{:.2f}'.format(turma_producao).replace('.', ','),
                                    '{:.2f}'.format(turma_multas).replace('.', ','),
                                    '{:.2f}'.format(turma_descontos).replace('.', ','),
                                    '{:.2f}'.format(turma_adesoes).replace('.', ',')]
            subtotal_realizado = ['','', '', '', 'VALOR PARA COMISSAO', '',
                                    '{:.2f}'.format(turma_parcelas + turma_descontos).replace('.', ',')]
            index += 1

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
        writer.writerow([rd.output_date()])


def execute_button():
    data_modeling()

    if button_income_table.getvar('PY_VAR0') == 1:
        output_income_table(start_date_input.get(), end_date_input.get())
    if button_comission_table.getvar('PY_VAR1') == 1:
        output_comission_table(start_date_input.get(), end_date_input.get())
    label_resultado['text']= 'Feito!'

def data_modeling():
    global filename
    data = DataCSV(filename)

    turma = data.access_column('turma')
    titulos = data.access_column('titulo')
    sacado = data.access_column('sacado')
    recebido = data.access_column('recebido')
    credito = data.access_column('credito')
    vencimento = data.access_column('vencimento')
    raw_descritivo = data.access_column('descritivo')

    "Redução de espaços excedentes"
    turma = rd.string_strip(turma)
    rd.include_semturma(turma)
    sacado = rd.string_strip(sacado)
    credito = rd.string_strip(credito)
    raw_descritivo = rd.string_strip(raw_descritivo)

    "Separação de linhas em elementos de uma lista"
    descritivo = rd.separate_lines(raw_descritivo, '\n')

    "Separação dos elementos da lista descritivo em colunas únicas"
    parcelas = rd.matcher_not_instr(descritivo)
    adesao = rd.matcher_instr(descritivo, 'ades')
    multas = rd.matcher_instr(descritivo, 'mult')
    producao = rd.matcher_instr(descritivo, 'prod')
    desconto = rd.matcher_instr(descritivo, 'desc')

    "Separação entre identificação da conta e o valor da conta"
    tipo_adesao, valor_adesao = rd.values_split(adesao)
    tipo_parcelas, valor_parcelas = rd.values_split(parcelas)
    tipo_multa, valor_multa = rd.values_split(multas)
    tipo_prod, valor_prod = rd.values_split(producao)
    tipo_desc, valor_desc = rd.values_split(desconto)

    "Inclusão de sinal negativo para identificação 'desconto'"
    rd.negative_values(tipo_desc, valor_desc)

    "Conversão em float para realização de cálculos"
    calc_adesao = data.col_str2numbers(valor_adesao)
    calc_multa = data.col_str2numbers(valor_multa)
    calc_parcelas = data.col_str2numbers(valor_parcelas)
    calc_prod = data.col_str2numbers(valor_prod)
    calc_desco = data.col_str2numbers(valor_desc)
    calc_receb = data.col_str2numbers(recebido)

    "Classificação de validade dos pagamentos"
    val_pgtos = rd.payment_validity(vencimento, start_date_input.get(), end_date_input.get())

    tb_columns = (turma, titulos, vencimento, sacado, val_pgtos, recebido, valor_parcelas,
                  valor_prod, valor_multa, valor_desc, valor_adesao, credito)

    calc_data = {
        'recebidos': calc_receb,
        'parcelas': calc_parcelas,
        'producao': calc_prod,
        'multas': calc_multa,
        'descontos': calc_desco,
        'adesao': calc_adesao
    }

    return tb_columns, calc_data

def open_file():
    global filename
    file_path = filedialog.askopenfilename(initialdir = getcwd(),title = "Select file",
                                           filetypes = (("extensão csv","*.csv"),("all files","*.*")))
    file_path = str(file_path).split('/')
    filename = file_path[-1]


# Definição da janela do programa
window = Tk()
window.wm_title('COMISSÃO - GALPÃO DO CIRCO')
window.geometry('460x390')
window.config(background='white')
logo_png = PhotoImage(file='logo_bolinha.png')
image_box = Canvas(width=110, height=110, bg='white', highlightthickness=0)
image_box.create_image(55,55, image=logo_png, anchor='center')

# Caixas de texto
label_filename = Label(text='1 - Selecione o arquivo .csv no campo abaixo', bg='white')
label_periodo = Label(text='''2 - Demarque o periodo do comissionamento incluindo as datas 
no campo abaixo. Use o formato dd/mm/aaaa''', justify='center', bg='white')
label_output = Label(text='3 - Escolha a informação que deseja extrair', bg='white')
label_resultado = Label(text='', bg='white', fg='green')

# Inputs
button_filename = Button(text="Escolha o arquivo", command=open_file)
start_date_input = Entry(justify='center', highlightcolor='orange', fg='blue')
end_date_input = Entry(justify='center', highlightcolor='orange',fg='red')

# Variáveis do checkbutton
income_button_variable = IntVar()
comission_button_variabe = IntVar()

# Botões
button_income_table = Checkbutton(text='Receita mensal', variable=income_button_variable,
                                  onvalue=1, offvalue=0, bg='white',activeforeground='blue')
button_comission_table = Checkbutton(text='Comissionamento', variable=comission_button_variabe,
                                     onvalue=1, offvalue=0, bg='white', activeforeground='blue')
button_execute = Button(text='Executar', command=execute_button)

window.group = {
    image_box.pack(),
    label_filename.pack(),
    button_filename.pack(),
    label_periodo.pack(),
    start_date_input.pack(),
    end_date_input.pack(),
    label_output.pack(),
    button_income_table.pack(),
    button_comission_table.pack(),
    button_execute.pack(),
    label_resultado.pack()
}

window.mainloop()
