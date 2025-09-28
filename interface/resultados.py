"""
Frame que apresenta o plano de refeicoes gerado, permitindo visualizar detalhes,
substituir/adicionar receitas, consultar lista de compras e gerir comentarios 
"""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from api.api_requests import obterDetalhesReceita, obterModoPreparo, substituicaoIngrediente, obterListaCompras, obterReceitas
from utils.nutricionais import valoresNutricionais
from utils.lista_compras import guardarListaCompras
from utils.favoritos import is_favorito, adicionar_favorito, remover_favorito
from interface.popup_receita import PopupAddSubReceita, PopupAdicionarReceita, PopupSubstituirReceita
from visual.cores import BACKGROUND
import random #necessario para randomizar offset e escolha

#Frame principal para apresentacao do plano de refeicoes
class ResultadosPlanoFrame(tk.Frame):
    def __init__(self, master, plano, ingredientes_disponiveis, api_key, dias_semana):
        super().__init__(master, bg=BACKGROUND)
        self.master = master
        self.plano = plano
        self.ingredientes_disponiveis = ingredientes_disponiveis
        self.api_key = api_key
        self.dias_semana = dias_semana
        self.tree = None
        self.receitas_exibidas_lista = []
        self.create_widgets()
    
    def create_widgets(self):
        tk.Label(self, text="Plano de Refeições", font=("Helvetica", 16)).pack(pady=10)
        frame_tree = tk.Frame(self, bg=BACKGROUND)
        frame_tree.pack(pady=10, fill="x", expand=True)

        self.ids_vistos = set()
        self.receitas_exibidas_lista = []

        #plano diario
        if "meals" in self.plano:
            columns = ("ID", "Título", "Duração (min)", "Doses", "Favorito")
            self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10)
            self.tree["displaycolumns"] = columns

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
            self.tree.pack(fill="x", expand=True)

            for meal in self.plano["meals"]:
                if meal["id"] not in self.ids_vistos:
                    self.ids_vistos.add(meal["id"])
                    fav_marker = "★" if is_favorito(meal["id"]) else ""
                    self.tree.insert("", "end", values=(meal["id"], meal["title"], meal.get("readyInMinutes", "N/A"), meal.get("servings", "N/A"), fav_marker))
                    self.receitas_exibidas_lista.append({"dia":"", "id":meal["id"], "title":meal["title"], "readyInMinutes":meal.get("readyInMinutes", "N/A"), "servings":meal.get("servings", "N/A")})
        #plano semanal
        elif "week" in self.plano:
            columns = ("Dia", "ID", "Título", "Duração (min)", "Doses", "Favorito")
            self.tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10)
            self.tree["displaycolumns"] = columns
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120)
            self.tree.pack(fill="x", expand=True)

            dias_ordenados = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for dia in dias_ordenados:
                info = self.plano["week"].get(dia)
                nome_dia = self.dias_semana.get(dia, dia.capitalize())

                if not info or not info.get("meals"):
                    self.tree.insert("", "end", values=(nome_dia, "-", "Sem sugestão", "-", "-", ""))
                    continue

                for meal in info["meals"]:
                    if meal["id"] not in self.ids_vistos:
                        self.ids_vistos.add(meal["id"])
                        fav_marker = "★" if is_favorito(meal["id"]) else ""
                        self.tree.insert("", "end", values=(nome_dia, meal["id"], meal["title"], meal.get("readyInMinutes", "N/A"), meal.get("servings", "N/A"), fav_marker))
                        self.receitas_exibidas_lista.append({"dia" : nome_dia, "id" : meal["id"], "title" : meal["title"], "readyInMinutes" : meal.get("readyInMinutes", "N/A"), "servings" : meal.get("servings", "N/A")})
        else:
            tk.Label(self, text="Plano inválido.", bg=BACKGROUND).pack()
            return
                                
        if not self.receitas_exibidas_lista:
            tk.Label(self, text="Nenhuma receita encontrada com os ingredientes disponíveis", bg=BACKGROUND).pack()

        frame_botoes = tk.Frame(self, bg=BACKGROUND)
        frame_botoes.pack(pady=10)
        tk.Button(frame_botoes, text="Ver Lista de Compras", command=self.mostrar_lista_compras).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Ver Detalhes", command=self.ver_detalhes).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Adicionar/Substituir Receita", command=self.adicionar_substituir_receita).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Favorito/Desfavoritar", command=self.toggle_favorito).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Voltar ao Menu", command=self.voltar_menu).pack(side="left", padx=10)

    def atualizar_treeview(self):
        #remove todas as linhas do treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        #Reinsere todas as receitas na lista exibida
        if "week" in self.plano:
            #plano semanal(6 colunas: Dia, Id, Titulo, Duracao, Doses, favorito)
            for receita in self.receitas_exibidas_lista:
                fav_marker = "★" if is_favorito(receita.get("id", "")) else ""
                values = (receita.get("dia", "-"), receita.get("id", "-"), receita.get("title", "-"), receita.get("readyInMinutes", "N/A"), receita.get("servings", "N/A"), fav_marker)
                self.tree.insert("", "end", values=values)
        else:
            #plano diario (5 colunas: ID, Titulo, Duracao, Doses, favorito)
            for receita in self.receitas_exibidas_lista:
                fav_marker = "★" if is_favorito(receita.get("id", "")) else ""
                values = (receita.get("id", "-"), receita.get("title", "-"), receita.get("readyInMinutes", "N/A"), receita.get("servings", "N/A"), fav_marker)
                self.tree.insert("", "end", values=values)

    def voltar_menu(self):
        from interface.menu_inicial import MenuInicial
        for widget in self.master.winfo_children():
            widget.destroy()
        MenuInicial(self.master).pack(fill="both", expand=True)
        
    def adicionar_substituir_receita(self):
        def callback_adicionar():
            PopupAdicionarReceita(self.master, self.adicionar_receita_callback)
        
        def callback_substituir(receita_id):
            self.substituir_receita_callback(receita_id)
        
        PopupAddSubReceita(self.master, self.receitas_exibidas_lista, callback_adicionar, callback_substituir)
    
    #adiciona uma nova receita manualmente ao plano e atualiza a interface
    def adicionar_receita_callback(self, titulo, receita_id, duracao, doses):
        #previne duplicados de ID
        for receita in self.receitas_exibidas_lista:
            if str(receita['id']) == str(receita_id):
                messagebox.showwarning("Duplicado", "Já existe uma receita com esse ID.")
                return

        #detecta se é plano semanal ou diario
        if "week" in self.plano:
            #tenta pedir o dia ao utilizador
            dias_opcoes = list(self.dias_semana.values())
            dia_selecionado = simpledialog.askstring("Dia da semana", f"Escolha o dia para a receita:\n{', '.join(dias_opcoes)}")
            if not dia_selecionado or dia_selecionado not in dias_opcoes:
                dia_selecionado = '-'
            nova_receita = {"dia": dia_selecionado, "id": receita_id if receita_id else f"manual_{titulo}", "title" : titulo, "readyInMinutes": duracao if duracao else "N/A", "servings": doses if doses else "N/A"}
        else:
            nova_receita = {"dia": "", "id": receita_id if receita_id else f"manual_{titulo}", "title" : titulo, "readyInMinutes" : duracao if duracao else "N/A", "servings": doses if doses else "N/A"}
        self.receitas_exibidas_lista.append(nova_receita)
        messagebox.showinfo("Nova Receita", f"Receita '{titulo}' adicionada ao plano!")
        self.atualizar_treeview()

    #substitui uma receita existente por uma receita nova sugerida via api
    def substituir_receita_callback(self, receita_id):
        #obter ids ja no plano para evitar repetiçoes
        ids_atual = set(str(r["id"]) for r in self.receitas_exibidas_lista)
        max_tentativas = 5
        nova_receita = None
        for _ in range(max_tentativas):
            offset = random.randint(0,50)
            nova_lista = obterReceitas([], self.api_key, numero_receitas=5, offset=offset)
            candidatas = [r for r in nova_lista if str(r["id"]) not in ids_atual]
            if candidatas:
                nova_receita = random.choice(candidatas) #escolhe aleatoriamente entre as nao repetidas
                break
        if not nova_receita:
            messagebox.showerror("Erro", "Não foi possível obter uma nova receita diferente para substituição.")
            return
        
        detalhes = obterDetalhesReceita(nova_receita["id"], self.api_key)
        nova_receita["readyInMinutes"] = detalhes.get("readyInMinutes", "N/A") if detalhes else "N/A"
        nova_receita["servings"] = detalhes.get("servings", "N/A") if detalhes else "N/A"
            
        #procura e substitui
        for idx, receita in enumerate(self.receitas_exibidas_lista):
            if str(receita["id"]) == str(receita_id):
                nova_receita["dia"] = receita.get("dia", "-")
                self.receitas_exibidas_lista[idx] = nova_receita
                messagebox.showinfo("Substituir Receita", f"A receita ID {receita_id} foi substituída por '{nova_receita['title']}'!")
                self.atualizar_treeview()
                break
        else:
            messagebox.showwarning("Não encontrada", "Receita não encontrada para substituição.")
    
    def ver_detalhes(self):
        selected_item = self.tree.focus()
        if selected_item:
            meal_data = self.tree.item(selected_item)["values"]
            receita_id = meal_data[1] if len(meal_data) == 6 else meal_data[0] #Coluna ID pode ser 1 ou 0 dependendo do plano
            self.mostrar_detalhes_receita(receita_id)
        else:
            messagebox.showwarning("Atenção", "Por favor selecione uma receita para obter detalhes.")   
    
    def mostrar_detalhes_receita(self, receita_id):
        for widget in self.master.winfo_children():
            widget.destroy()
        DetalhesReceitaFrame(self.master, receita_id=receita_id, plano=self.plano, api_key=self.api_key, ingredientes_disponiveis=self.ingredientes_disponiveis, dias_semana=self.dias_semana).pack(fill="both", expand=True)
    
    def mostrar_lista_compras(self):
        from datetime import datetime
        from interface.listas_compras import ListaComprasVisualizacaoFrame

        receitas_formatadas = []
        for r in self.receitas_exibidas_lista:
            receitas_formatadas.append({"id": r.get("id", ""), "title" : r.get("title", ""), "readyInMinutes" : r.get("readyInMinutes", "N/A"), "servings" : r.get("servings", "N/A"), "dia" : r.get("dia", "")})
        lista_ingredientes = obterListaCompras(receitas_formatadas, self.api_key)
        
        identificador = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guardarListaCompras(lista_ingredientes, identificador)

        def voltar_para_resultados():
            for widget in self.master.winfo_children():
                widget.destroy()
            ResultadosPlanoFrame(self.master, plano=self.plano, ingredientes_disponiveis=self.ingredientes_disponiveis, api_key=self.api_key, dias_semana=self.dias_semana).pack(fill="both", expand=True)
        
        for widget in self.master.winfo_children():
            widget.destroy()
        ListaComprasVisualizacaoFrame(self.master, lista_ingredientes, voltar_para_resultados).pack(fill="both", expand=True)

    #funcao para alterar favorito
    def toggle_favorito(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Atenção", "Por favor selecione uma receita para marcar/desmarcar como favorito.")
            return
        meal_data = self.tree.item(selected_item)["values"]
        receita_id = meal_data[1] if len(meal_data) == 6 else meal_data[0]
        if is_favorito(receita_id):
            remover_favorito(receita_id)
            messagebox.showinfo("Favoritos", "Receita removida dos favoritos.")
            self.atualizar_treeview()
        else:
            adicionar_favorito(receita_id)
            messagebox.showinfo("Favoritos", "Receita adicionada aos favoritos.")
            self.atualizar_treeview()

        
#Frame para apresentacao dos detalhes de uma receita especifica.
#Permite ver ingredientes, modo de preparo, valores nutricionais, comentarios e sugestoes de substituicoes de ingredientes
class DetalhesReceitaFrame(tk.Frame):
    def __init__(self, master, receita_id, plano, api_key, ingredientes_disponiveis, dias_semana):
        super().__init__(master, bg=BACKGROUND)
        self.master = master
        self.receita_id = receita_id
        self.plano = plano
        self.api_key = api_key
        self.ingredientes_disponiveis = ingredientes_disponiveis
        self.dias_semana = dias_semana
        self.create_widgets()
    
    def create_widgets(self):
        #scrollable Frame
        canvas = tk.Canvas(self, bg=BACKGROUND)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=BACKGROUND)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        detalhes = obterDetalhesReceita(self.receita_id, self.api_key)
        if not detalhes:
            messagebox.showerror("Erro", "Detalhes da receita não disponíveis.")
            self.voltar_resultados()
            return
        
        tk.Label(scroll_frame, text=detalhes['title'], font=("Helvetica", 16), bg=BACKGROUND).pack(pady=10)
        tk.Label(scroll_frame, text=f"Tempo de preparo: {detalhes.get('readyInMinutes', 'N/A')} min", bg=BACKGROUND).pack()
        tk.Label(scroll_frame, text=f"Doses: {detalhes.get('servings', 'N/A')}", bg=BACKGROUND).pack()

        #valores nutricionais 
        nutricion_data = detalhes.get('nutrition', {})
        if nutricion_data:
            calorias, proteinas, gorduras, hidratos = valoresNutricionais(nutricion_data)
            tk.Label(scroll_frame, text=f"Valores Nutricionais: {calorias} kcal | {proteinas} proteina | {gorduras} gordura | {hidratos} hidratos", bg=BACKGROUND).pack(pady=5)
        else:
            tk.Label(scroll_frame, text="Informação nutricional não disponível.", bg=BACKGROUND).pack(pady=5)
        
        #ingredientes
        ingredientes_frame = tk.LabelFrame(scroll_frame, text="Ingredientes necessários", font=("Helvetica", 12, "bold"), padx=10, pady=10, bg=BACKGROUND)
        ingredientes_frame.pack(padx=20, pady=10, fill="x")
        for ing in detalhes.get('extendedIngredients', []):
            tk.Label(ingredientes_frame, text=f" - {ing['name']}", bg=BACKGROUND).pack(anchor="w")
        
        #modo preparo
        modo_preparo = obterModoPreparo(self.receita_id, self.api_key)
        if modo_preparo:
            tk.Label(scroll_frame, text="Modo de Preparo:", font=("Helvetica", 12, "bold"), bg=BACKGROUND).pack(pady=5)
            for instrucao in modo_preparo:
                for passo in instrucao.get('steps', []):
                    frame_passo = tk.Frame(scroll_frame, bg=BACKGROUND)
                    frame_passo.pack(anchor="w", padx=20, pady=2)
                    tk.Label(frame_passo, text=f"Etapa {passo['number']}:", font=("Helvetica", 10, "bold"), bg=BACKGROUND).pack(side="left")
                    tk.Label(frame_passo, text=f" {passo['step']}", wraplength=700, justify="left", bg=BACKGROUND).pack(side="left")
        else:
            tk.Label(scroll_frame, text="Modo de preparo não disponível.", bg=BACKGROUND).pack()
        
        # Comentários
        tk.Label(scroll_frame, text="Comentários:", font=("Helvetica", 12, "bold"), bg=BACKGROUND).pack(pady=5)
        from utils.comentarios import lerComentarios
        comentarios = lerComentarios(self.receita_id)
        if comentarios:
            for c in comentarios:
                tk.Label(scroll_frame, text=f" - {c['utilizador']}: {c['comentario']}", bg=BACKGROUND).pack(anchor="w", padx=20)
        else:
            tk.Label(scroll_frame, text="Ainda não existem comentários sobre esta receita.", bg=BACKGROUND).pack()

        # Botões de interação
        tk.Button(scroll_frame, text="Adicionar Comentário", command=self.abrir_formulario_comentario).pack(pady=10)
        tk.Button(scroll_frame, text="Substituir Ingrediente", command=self.abrir_formulario_substituicao).pack(pady=5)
        tk.Button(scroll_frame, text="Voltar para Refeições", command=self.voltar_resultados).pack(pady=10)

    def abrir_formulario_comentario(self):
        nova_janela = tk.Toplevel(self)
        nova_janela.title("Adicionar Comentário")

        tk.Label(nova_janela, text="Nome:").grid(row=0, column=0, padx=10, pady=5)
        nome_entry = tk.Entry(nova_janela)
        nome_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(nova_janela, text="Comentário: ").grid(row=1, column=0, padx=10, pady=5)
        comentario_entry = tk.Entry(nova_janela, width=50)
        comentario_entry.grid(row=1, column=1, padx=10, pady=5)
    
        def guardar():
            nome = nome_entry.get()
            comentario = comentario_entry.get()
            if nome and comentario:
                from utils.comentarios import guardarComentario
                guardarComentario(self.receita_id, comentario, nome)
                messagebox.showinfo("Sucesso", "Comentário guardado com sucesso.")
                nova_janela.destroy()
                self.reload()
            else:
                messagebox.showwarning("Campos obrigatórios", "Por favor, preencha o nome e adicione um comentário.")

        tk.Button(nova_janela, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

    def abrir_formulario_substituicao(self):
        nova_janela = tk.Toplevel(self)
        nova_janela.title("Substituir Ingrediente")

        tk.Label(nova_janela, text="Ingrediente a substituir: ").grid(row=0, column=0, padx=10, pady=5)
        ingredientes_entry = tk.Entry(nova_janela)
        ingredientes_entry.grid(row=0, column=1, padx=10, pady=5)

        sugestoes_text = tk.Text(nova_janela, height=10, width=50)
        sugestoes_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        def sugerir():
            ingrediente = ingredientes_entry.get().strip().lower()
            if not ingrediente:
                messagebox.showwarning("Campo vazio", "Por favor, insira o nome de um ingrediente.")
                return
            sugestoes_text.delete("1.0", tk.END)
            try:
                sugestoes = substituicaoIngrediente(ingrediente, self.api_key)
                if sugestoes:
                    for s in sugestoes:
                        sugestoes_text.insert(tk.END, f" - {s}\n")
                else:
                    sugestoes_text.insert(tk.END, f"Nenhuma sugestão disponível para '{ingrediente}'.")
            except Exception as e:
                sugestoes_text.insert(tk.END, f"Erro ao buscar substituições: {str(e)}")

        tk.Button(nova_janela, text="Sugerir Substituições", command=sugerir).grid(row=1, column=0, columnspan=2, pady=5)
    
    def voltar_resultados(self):
        from interface.resultados import ResultadosPlanoFrame
        for widget in self.master.winfo_children():
            widget.destroy()
        ResultadosPlanoFrame(self.master, plano=self.plano, ingredientes_disponiveis=self.ingredientes_disponiveis, api_key=self.api_key, dias_semana=self.dias_semana).pack(fill="both", expand=True)
        
    
    def reload(self):
        for widget in self.master.winfo_children():
            widget.destroy()
        DetalhesReceitaFrame(self.master, receita_id=self.receita_id, plano=self.plano, api_key=self.api_key, ingredientes_disponiveis=self.ingredientes_disponiveis, dias_semana=self.dias_semana).pack(fill="both", expand=True)
