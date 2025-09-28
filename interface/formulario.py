"""
Frame responsavel pela criação de um novo plano de refeicoes
Permite ao utilizador escolher tipo de dieta, calorias, periodo e ingredientes disponiveis 
e gera um plano ajustado às preferencias
"""
import tkinter as tk
from tkinter import ttk, messagebox
from api.api_requests import planoRefeicoes, obterDetalhesReceita
from utils.historico import guardarPlanoHistorico
from utils.nutricionais import valoresNutricionais
from visual.cores import BACKGROUND

#Frame Tkinter para o formulario de criacao de planos
class FormularioPlanoFrame(tk.Frame):
    #Inicializa o formulario de plano de refeicoes
    def __init__(self, master):
        super().__init__(master, bg=BACKGROUND)
        self.api_key = self.carregar_api_key()
        self.dias_semana = self.carregar_dias_semana()
        self.ingredientes_disponiveis = []
        self.create_widgets()
    
    #Carrega a chave da API a partir do ficheiro de configuracao
    def carregar_api_key(self):
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        api_key_path = os.path.join(base_path, "..", "Config", "api_key.txt")
        with open(api_key_path, "r") as f:
            return f.read().strip()
    
    #carrega o dicionario de nomes dos dias da semana em portugues
    def carregar_dias_semana(self):
        import os, json
        base_path = os.path.dirname(os.path.abspath(__file__))
        dias_path = os.path.join(base_path, "..", "Config", "dias_semana_pt.json")
        with open(dias_path, "r", encoding="utf-8") as f:
            return json.load(f)
    #cria todos os widgets do formulario para definicao do plano
    def create_widgets(self):
        tk.Label(self, text="Criar Novo Plano de Refeições", font=("Helvetica", 16), bg=BACKGROUND).pack(pady=10)
        
        frame_inputs = tk.Frame(self, bg=BACKGROUND)
        frame_inputs.pack(pady=20)

        #dieta 
        tk.Label(frame_inputs, text="Dieta:", bg=BACKGROUND).grid(row=0, column=0, padx=5, pady=5)
        self.dieta_var = tk.StringVar()
        self.dieta_combobox = ttk.Combobox(frame_inputs, textvariable=self.dieta_var, values=["Vegetarian", "Vegan", "Gluten Free", "Ketogenic", "Pescetarian", "Paleo"])
        self.dieta_combobox.grid(row=0, column=1, padx=5, pady=5)

        #calorias
        tk.Label(frame_inputs, text="Calorias:", bg=BACKGROUND).grid(row=1, column=0, padx=5, pady=5)
        self.calorias_entry = tk.Entry(frame_inputs)
        self.calorias_entry.grid(row=1, column=1, padx=5, pady=5)

        #periodo
        tk.Label(frame_inputs, text="Período:", bg=BACKGROUND).grid(row=2, column=0, padx=5, pady=5)
        self.periodo_var = tk.StringVar(value="day")
        periodo_menu = ttk.Combobox(frame_inputs, textvariable=self.periodo_var, values=["day", "week"])
        periodo_menu.grid(row=2, column=1, padx=5, pady=5)

        #Ingredientes necessarios
        tk.Label(frame_inputs, text="Ingredientes disponíveis (separados por virgulas):", bg=BACKGROUND).grid(row=3, column=0, columnspan=2, pady=10)
        self.ingredientes_entry = tk.Entry(frame_inputs, width=50)
        self.ingredientes_entry.grid(row=4, column=0, columnspan=2)

        #botoes
        button_frame = tk.Frame(self, bg=BACKGROUND)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Gerar Plano", command=self.gerar_plano).pack(side="left", padx=10)
        tk.Button(button_frame, text="Voltar", command=self.voltar).pack(side="left",padx=10)
    
    #Gera o plano de refeicoes com base nos inputs do utilizador, filtra receitas que usem os ingredientes disponiveis
    def gerar_plano(self):
        time_frame = self.periodo_var.get()
        target_calories = self.calorias_entry.get()
        dieta = self.dieta_combobox.get()
        ingredientes_text = self.ingredientes_entry.get()

        try:
            target_calories = int(target_calories) if target_calories else None
        except ValueError:
            messagebox.showerror("Erro", "As calorias devem ser um número válido!")
            return
        #lista de ingredientes disponiveis normalizada
        self.ingredientes_disponiveis = [ing.strip().lower() for ing in ingredientes_text.split(",") if ing.strip()]

        plano = planoRefeicoes(self.api_key, time_frame, target_calories, dieta)
        if plano and ("meals" in plano or "week" in plano):
            refeicoes_validas = []
            #extrai refeicoes do plano diario ou semanal
            refeicoes = plano["meals"] if "meals" in plano else [meal for dia in plano["week"].values() for meal in dia["meals"]]
            for meal in refeicoes:
                detalhes = obterDetalhesReceita(meal["id"], self.api_key)
                if detalhes:
                    ingredientes_receita = [ing["name"].lower() for ing in detalhes.get("extendedIngredients", [])]
                    #so adiciona refeicoes que usem pelo menos um ingrediente disponivel
                    if not self.ingredientes_disponiveis or set(self.ingredientes_disponiveis) & set(ingredientes_receita):
                        refeicoes_validas.append(meal)
            
            if not refeicoes_validas:
                messagebox.showerror("Erro", "Nenhuma receita encontrada com os dados fornecidos.")
                return
            guardarPlanoHistorico(plano, dieta, target_calories)
            self.mostrar_resultado(plano)
        else:
            messagebox.showerror("Erro", "Não foi possível gerar o plano de refeições. Verifique as suas preferências.")
    #Mostra o resultado do plano gerado, trocando para o frame de resultados
    def mostrar_resultado(self, plano):
        #importacao tardia para evitar ciclos
        from interface.resultados import ResultadosPlanoFrame
        for widget in self.master.winfo_children():
            widget.destroy()
        ResultadosPlanoFrame(self.master, plano=plano, ingredientes_disponiveis=self.ingredientes_disponiveis, api_key=self.api_key, dias_semana=self.dias_semana).pack(fill="both", expand= True)

    #Volta ao menu inicial, destruindo os widgets atuais
    def voltar(self):
        from interface.menu_inicial import MenuInicial
        for widget in self.master.winfo_children():
            widget.destroy()
        MenuInicial(self.master).pack(fill="both", expand=True)
        