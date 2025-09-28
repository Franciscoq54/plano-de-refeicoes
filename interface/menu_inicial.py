"""
Frame inicial da aplicacao Planeador de Refeicoes
Permite ao utilizador navegar para o historico de planos, listas de compras anteriores ou criar um novo plano
"""
import tkinter as tk
from tkinter import messagebox
from interface.historico import HistoricoFrame
from interface.listas_compras import ListasComprasFrame
from interface.formulario import FormularioPlanoFrame
from visual.cores import PRIMARY, BACKGROUND, BUTTON_TEXT, EXIT
from visual.estilos import aplicar_estilos
from visual.recursos import carregar_imagem

#Frame inicial da aplicacao para navegar entre as funcionalidades principais
class MenuInicial(tk.Frame):
    #Inicializa o menu inicial
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        aplicar_estilos()
        self.create_widgets()
    #cria e organiza os widgets do menu inicial
    def create_widgets(self):
        banner = carregar_imagem("banner_refeicoes.jpg", tamanho=(400, 120))
        if banner:
            tk.Label(self, image=banner, bg=BACKGROUND).pack(pady=(15, 5))
            self.banner = banner #manter referencia para evitar garbage collect
        tk.Label(self, text="Bem-vindo ao Planeador de Refeições", font=("Helvetica", 18, "bold"), bg=BACKGROUND, fg=PRIMARY).pack(pady=20)
        
        tk.Button(self, text="Visualizar Planos Anteriores", font=("Helvetica", 12, "bold"), command=self.mostrar_historicos).pack(pady=10)
        tk.Button(self, text="Visualizar Listas de Compras Anteriores",font=("Helvetica", 12, "bold"), command=self.mostrar_listas_compras).pack(pady=10)
        tk.Button(self, text="Criar Novo Plano", font=("Helvetica", 12, "bold"), command=self.mostrar_formulario).pack(pady=10)
        tk.Button(self, text="Sair", font=("Helvetica", 12), bg=EXIT, fg=BUTTON_TEXT, command=self.sair).pack(pady=20)

    #Troca o frame para visualizacao do historico de planos
    def mostrar_historicos(self):
        self._trocar_frame(HistoricoFrame)
    #troca o frame para visualizacao das listas de compras anteriores
    def mostrar_listas_compras(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        ListasComprasFrame(self.master).pack(fill="both", expand=True)
    #troca o frame para o formulario de criacao de um novo plano
    def mostrar_formulario(self):
        self._trocar_frame(FormularioPlanoFrame)
    
    #Troca o frame atual pelo fornecido
    def _trocar_frame(self, FrameClass):
        for widget in self.master.winfo_children():
            widget.destroy()
        FrameClass(self.master).pack(fill="both", expand= True)
    
    #metodo para sair da aplicacao
    def sair(self):
        if messagebox.askokcancel("Sair", "Deseja mesmo sair da aplicação?"):
            self.master.destroy()
    