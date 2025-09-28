"""
Modulo com popups para adicionar ou substituir receitas no plano, usando Tkinter
"""
import tkinter as tk
from tkinter import ttk, messagebox
from visual.cores import BACKGROUND

#Popup para escolher entre adicionar uma nova receita ou substituir uma existente
class PopupAddSubReceita(tk.Toplevel):
    #Inicializa o popup de escolha 
    def __init__(self, master, receitas_lista, callback_adicionar, callback_substituir):
        super().__init__(master)
        self.title("Adicionar ou Substituir Receita")
        self.geometry("350x180")
        self.configure(bg=BACKGROUND)
        self.callback_adicionar = callback_adicionar
        self.callback_substituir = callback_substituir
        self.receitas_lista = receitas_lista

        tk.Label(self, text="O que pretende fazer?", font=("Helvetica", 12), bg=BACKGROUND).pack(pady=10)
        frame_botoes = tk.Frame(self, bg=BACKGROUND)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Adicionar Receita", width=14, command=self._adicionar).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Substituir Receita", width=15, command=self._substituir).pack(side="left", padx=10)
    
    def _adicionar(self):
        self.destroy()
        self.callback_adicionar()

    def _substituir(self):
        self.destroy()
        PopupSubstituirReceita(self.master, self.receitas_lista, self.callback_substituir)

#Popup para adicionar uma nova receita ao plano
class PopupAdicionarReceita(tk.Toplevel):
    #Inicializa o popup de adicao de receita
    def __init__(self, master, callback_adicionar):
        super().__init__(master)
        self.title("Adicionar Receita ao Plano")
        self.geometry("400x400")
        self.configure(bg=BACKGROUND)
        self.callback_adicionar = callback_adicionar

        tk.Label(self, text="Adicionar uma nova receita", font=("Helvetica", 12, "bold"), bg=BACKGROUND).pack(pady=10)
        tk.Label(self, text="Título da Receita:", bg=BACKGROUND).pack()
        self.titulo_entry = tk.Entry(self, width=40)
        self.titulo_entry.pack(pady=5)
        tk.Label(self, text="ID (opcional):", bg=BACKGROUND).pack()
        self.id_entry= tk.Entry(self, width=20)
        self.id_entry.pack(pady=5)
        tk.Label(self, text="Duração (min):", bg=BACKGROUND).pack()
        self.duracao_entry = tk.Entry(self, width=20)
        self.duracao_entry.pack(pady=5)
        tk.Label(self, text="Doses:", bg=BACKGROUND).pack()
        self.doses_entry = tk.Entry(self, width=20)
        self.doses_entry.pack(pady=5)

        tk.Button(self, text="Adicionar", command=self._adicionar).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.destroy).pack()
        
    def _adicionar(self):
        titulo = self.titulo_entry.get().strip()
        receita_id = self.id_entry.get().strip()
        duracao = self.duracao_entry.get()
        doses = self.doses_entry.get()
        if not titulo:
            messagebox.showwarning("Atenção", "Por favor, preencha o título da receita.")
            return
        self.callback_adicionar(titulo, receita_id, duracao, doses)
        self.destroy()

#Popup para escolher uma receita existente do plano a ser substituida
class PopupSubstituirReceita(tk.Toplevel):
    #Inicializa o popup de substituicao
    def __init__(self, master, receitas_lista, callback_substituir):
        super().__init__(master)
        self.title("Substituir Receita do Plano")
        self.geometry("400x200")
        self.configure(bg=BACKGROUND)
        self.callback_substituir = callback_substituir

        tk.Label(self, text="Selecione a receita do plano que deseja substituir:", font=("Helvetica", 11, "bold"), bg=BACKGROUND).pack(pady=10)
        if not receitas_lista:
            tk.Label(self, text="Nenhuma receita disponível para substituir.", bg=BACKGROUND).pack(pady=10)
            tk.Button(self, text="Fechar", command=self.destroy).pack(pady=10)
            return

        receitas_dict = {f"{m['title']} (ID: {m['id']})": m['id'] for m in receitas_lista}
        receitas_nomes = list(receitas_dict.keys())

        self.selected = tk.StringVar()
        combo = ttk.Combobox(self, values=receitas_nomes, textvariable=self.selected, state="readonly", width=35)
        combo.pack(pady=10)

        def substituir():
            receita_str = self.selected.get()
            if not receita_str:
                messagebox.showwarning("Aviso", "Selecione uma receita para substituir.")
                return
            receita_id = receitas_dict[receita_str]
            self.callback_substituir(receita_id)
            self.destroy()

        tk.Button(self, text="Substituir", command=substituir).pack(pady=10)
        tk.Button(self, text="Cancelar", command=self.destroy).pack(pady=5)