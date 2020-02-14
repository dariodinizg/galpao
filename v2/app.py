from tkinter import *
from tkinter import filedialog
from os import getcwd

import os
import sys
sys.path.append(os.getcwd())

from data_engineer import DataEngineer
from config_manager import ConfigManager
from datetime import datetime


class AppGui:
    
    def __init__(self):
        self.window = Tk()

    def create_widgets(self):
        # Labels
        self.label_choose_file = Label(
            self.window,
            text='1 - Selecione o arquivo .XLS gerado pelo SOPHIA   ', 
            bg='white', 
            justify='left',
            )
        self.label_periodo = Label(
            self.window,
            text='2 - Periodo do comissionamento. Use o formato dd/mm/aaaa', 
            justify=LEFT, 
            bg='white',
            wraplength=0
            )
        self.label_de = Label(self.window, text='de', justify=CENTER, pady=-1, bg='white')
        self.label_ate = Label(self.window, text='ate', justify=CENTER, pady=-1, bg='white')
        self.label_output = Label(self.window, text='3 - Escolha a informação que deseja extrair', bg='white')
        self.label_aviso = Label(
            self.window, 
            text='', 
            bg='white', 
            fg='green', 
            justify=LEFT, 
            borderwidth=3, 
            relief="groove", 
            width=47)

        # Variáveis do checkbutton
        self.income_button_variable = IntVar()
        self.comission_button_variabe = IntVar()
       
        # Buttons
        self.button_openfile = Button(self.window, text="Escolha o arquivo", command=self.open_file, height=0, pady=-1, padx=100)
        self.button_income_table = Checkbutton(
            self.window,
            text='Comissionamento', 
            variable=self.income_button_variable,
            onvalue=1, 
            offvalue=0, 
            bg='white',
            activeforeground='blue',
            width=15
            )
        self.button_comission_table = Checkbutton(
            self.window,
            text='Receita Mensal', 
            variable=self.comission_button_variabe,
            onvalue=1, 
            offvalue=0, 
            bg='white', 
            activeforeground='blue',
            width=15
            )
        self.button_execute = Button(self.window,text='Executar', command=self.execute_button, bg="purple", fg='white', padx=130)
        
        # Inputs
        self.start_date_input = Entry(self.window, justify='center', highlightcolor='orange', fg='blue', width=18)
        self.end_date_input = Entry(self.window, justify='center', highlightcolor='orange',fg='red', width=18)
        
        # Display logo
        self.logo_png = PhotoImage(file='logo_bolinha.png')
        self.logo_image_box = Canvas(width=210, height=210, bg='white', highlightthickness=0)
        self.logo_image_box.create_image(105,105, image=self.logo_png, anchor='center')
    
    def execute_button(self):
        try:
            de = DataEngineer(self.filename, *self.get_comission_date())
            # bool(self.filename)
        except AttributeError:
            self.label_aviso.config(text='Erro ao ler arquivo XLS', bg='white', fg='red')
        if not de.is_dataset_right():
            self.label_aviso.config(text='Formato XLS inválido. Verifique estrutura do relatório', bg='white', fg='red')
        export_comission = False
        export_incomes = False
        comission_button = self.button_income_table.getvar('PY_VAR0')
        incomes_button = self.button_comission_table.getvar('PY_VAR1')
        if comission_button == 0 and incomes_button == 0:
            self.label_aviso.config(text='Nenhuma opção foi selecionada', bg='white', fg='red')
        else:
            if comission_button == 1:
                export_comission = True
            if incomes_button == 1:
                export_incomes = True
                de.run(export_comission,export_incomes)
                self.label_aviso.config(text=de.app_warning.text, bg=de.app_warning.bg, fg=de.app_warning.fg)
    
    def get_comission_date(self):
        start_date = self.start_date_input.get()
        end_date = self.end_date_input.get()
        try:
            self.start_date = datetime.strptime(start_date, '%d/%m/%Y').date()
            self.end_date = datetime.strptime(end_date, '%d/%m/%Y').date()
        except ValueError:
            self.label_aviso.config(text='Formato de datas inválido', bg='white', fg='red')
        return start_date, end_date

    def load_configuration(self):
        settings = ConfigManager('general_config.json').settings
        extensions = settings['extension']
        return extensions

    def open_file(self):
        extensions = self.load_configuration()
        self.filename = filedialog.askopenfilename(initialdir = getcwd(),title = "Select file",
                                        filetypes = ((extensions),("all files","*.*"))
                                        )

    def position_widgets(self):
        self.logo_image_box.grid(row=0, column=0, rowspan=10, pady=2)
        self.label_choose_file.grid(row=2, column=1, sticky=W, pady=2)
        self.button_openfile.grid(row=2, column=4, columnspan=2, sticky=W, pady=2, padx=10)
        self.label_de.grid(row=3, column=4, padx=1)
        self.label_ate.grid(row=3, column=5, padx=1)
        self.label_periodo.grid(row=4, column=1, sticky=W, columnspan=3, pady=2)
        self.start_date_input.grid(row=4, column=4, pady=2, padx=1)
        self.end_date_input.grid(row=4, column=5, pady=2)
        self.label_output.grid(row=5, column=1, sticky=W, pady=2)
        self.button_income_table.grid(row=5, column=4, pady=2)
        self.button_comission_table.grid(row=5, column=5, pady=2)
        self.button_execute.grid(row=6, column=4, columnspan=2, sticky=W, pady=2, padx=10)
        self.label_aviso.grid(row=6, column=1, columnspan=3, pady=2, sticky=W)

    def run(self):
        self.create_widgets()
        self.format_window()
        self.position_widgets()
        self.window.mainloop()

    def format_window(self):
        self.window.wm_title('COMISSÃO - GALPÃO DO CIRCO')
        self.window.geometry('965x220')
        self.window.minsize(965,220)
        self.window.maxsize(965,220)
        self.window.config(background='white')
        
        
if __name__=='__main__':
    AppGui().run()