import tkinter as tk
import json
from tkinter import ttk, messagebox
from api.api_requests import planoRefeicoes, obterDetalhesReceita, obterModoPreparo, obterListaCompras
from utils.comentarios import guardarComentario, mostrarComentarios
from utils.historico import guardarPlanoHistorico, mostrarHistorico
from utils.nutricionais import valoresNutricionais

API_KEY = "5c6f3108b2c34e5d9eb78b8b82a1e4e6"
ingredientes_disponiveis = []

#configuracao principal da janela
root = tk.Tk()
root.title("Planeador de Refeições")
root.geometry("800x600")

def mostrar_menu_inicial():
    global ingredientes_disponiveis
    ingredientes_disponiveis = [] #limpa ingredientes antigos
    #Limpar janela
    for widget in root.winfo_children():
        widget.destroy()
    #criar os botoes principais
    tk.Label(root, text= "Bem-vindo ao Planeador de refeições", font=("Helvetica", 16)).pack(pady=20)
    tk.Button(root, text="Visualizar Planos Anteriores", command=mostrar_historico).pack(pady=10)
    tk.Button(root, text="Criar Novo Plano", command=mostrar_formulario).pack(pady=10)

def mostrar_historico():
    #limpar a janela
    for widget in root.winfo_children():
        widget.destroy()
    
    #mostrar o historico
    tk.Label(root, text="Histórico de Planos de Refeições", font=("Helvetica", 16)).pack(pady=10)
    historico_text = tk.Text(root, height=20, width=80)
    historico_text.pack(padx=10, pady=10)

    historico = mostrarHistorico()
    if not historico:
        historico_text.insert(tk.END, "Nenhum plano de refeições foi guardado ainda.")
    else:
        for plano in historico:
            historico_text.insert(tk.END, f"Data: {plano['data']}\n")
            historico_text.insert(tk.END, f"Dieta: {plano['dieta']}\n")
            historico_text.insert(tk.END, f"Calorias: {plano['calorias']}\n")
            historico_text.insert(tk.END, "Refeições:\n")
            for meal in plano["meals"]:
                historico_text.insert(tk.END, f" - {meal}\n")
            historico_text.insert(tk.END, "\n") 

    #botao para voltar ao menu inicial 
    tk.Button(root,text="Voltar", command=mostrar_menu_inicial).pack(pady=10)

def mostrar_formulario():
    global periodo_var, calorias_entry, dieta_combobox, ingredientes_entry
    #limpar janela
    for widget in root.winfo_children():
        widget.destroy()
    #criar formulario
    tk.Label(root, text="Criar Novo Plano de Refeições", font=("Helvetica", 16)).pack(pady=10)

    frame_inputs = tk.Frame(root)
    frame_inputs.pack(pady=20)

    tk.Label(frame_inputs, text="Dieta:").grid(row=0, column=0, padx=5, pady=5)
    dieta_var = tk.StringVar()
    dieta_combobox = ttk.Combobox(frame_inputs, textvariable=dieta_var, values=["Vegetarian", "Vegan", "Gluten Free", "Ketogenic", "Pescetarian", "Paleo"])
    dieta_combobox.grid(row=0, column=1, padx=5, pady=5)
   
    tk.Label(frame_inputs, text="Calorias:").grid(row=1, column=0, padx=5, pady=5)
    calorias_entry = tk.Entry(frame_inputs)
    calorias_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Período:").grid(row=2, column=0, padx=5, pady=5)
    periodo_var = tk.StringVar(value="day")
    periodo_menu = ttk.Combobox(frame_inputs, textvariable=periodo_var, values=["day", "week"])
    periodo_menu.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Ingredientes disponíveis (separados por vírgula):").grid(row=3, column=0, columnspan=2, pady=10)
    ingredientes_entry = tk.Entry(frame_inputs, width=50)
    ingredientes_entry.grid(row=4, column=0, columnspan=2)

    tk.Button(root, text="Gerar Plano", command=gerar_plano).pack(pady=10)
    tk.Button(root, text="Voltar", command=mostrar_menu_inicial).pack(pady=10)

def gerar_plano():
    global ingredientes_disponiveis
    time_frame = periodo_var.get()
    target_calories = calorias_entry.get()
    dieta = dieta_combobox.get()
    ingredientes_text = ingredientes_entry.get()

    try:
        target_calories = int(target_calories) if target_calories else None
    except ValueError:
        messagebox.showerror("Erro", "As calorias devem ser um número válido!")
        return
    
    #guardar ingredientes disponiveis como lista
    ingredientes_disponiveis = [ing.strip().lower() for ing in ingredientes_text.split(",") if ing.strip()]
    
    plano = planoRefeicoes(API_KEY, time_frame, target_calories, dieta)
    if plano and ("meals" in plano or "week" in plano):
        refeicoes_validas = []
        refeicoes = plano["meals"] if "meals" in plano else [meal for dia in plano["week"].values() for meal in dia["meals"]]
        for meal in refeicoes:
            detalhes = obterDetalhesReceita(meal["id"], API_KEY)
            if detalhes:
                ingredientes_receita = [ing["name"].lower() for ing in detalhes.get("extendedIngredients", [])]
                if not ingredientes_disponiveis or set(ingredientes_disponiveis) & set(ingredientes_receita):
                    refeicoes_validas.append(meal)
        
        if not refeicoes_validas:
            messagebox.showerror("Erro", "Nenhuma receita encontrada com os dados fornecidos.")
            return
        
        #verifica se ha pelo menos uma receita que sera exibida
        guardarPlanoHistorico(plano, dieta, target_calories)
        mostrar_resultados(plano)
    else:
        messagebox.showerror("Erro", "Não foi possível gerar o plano de refeições. Verifique as suas preferências.")
    
def mostrar_resultados(plano):
    global tree
    for widget in root.winfo_children():
        widget.destroy()

#mostrar os resultados
    tk.Label(root, text="Plano de refeições", font=("Helvetica", 16)).pack(pady=10)
    # Treeview para exibir refeições
    frame_tree = tk.Frame(root)
    frame_tree.pack(pady=10)

    columns = ("ID", "Título", "Duração (min)", "Porções")
    tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack()

    receitas_exibidas = 0
    refeicoes = []

    if "meals" in plano:
        #plano diario
        refeicoes = plano["meals"]
    elif "week" in plano:
        #plano semanal
        for dia in plano["week"].values():
            for meal in dia.get("meals", []):
                refeicoes.append(meal)

    for meal in refeicoes:
        detalhes = obterDetalhesReceita(meal["id"], API_KEY)
        if detalhes:
            ingredientes_receita = [ing["name"].lower() for ing in detalhes.get("extendedIngredients", [])]
            if not ingredientes_disponiveis or set(ingredientes_disponiveis) & set(ingredientes_receita):
                tree.insert("", "end", values=(meal["id"], meal["title"], meal["readyInMinutes"], meal["servings"]))
                receitas_exibidas += 1
    
    if receitas_exibidas == 0:
        tk.Label(root, text="Nenhuma receita encontrada com os ingredientes disponíveis.").pack()

    #botoes para ver detalhes e voltar
    frame_botoes = tk.Frame(root)
    frame_botoes.pack(pady=10)
    tk.Button(frame_botoes, text="Ver Detalhes", command=lambda: ver_detalhes(plano)).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Voltar", command=mostrar_menu_inicial).pack(side="left", padx=10)

def ver_detalhes(plano):
    selected_item = tree.focus()
    if selected_item:
        meal_data = tree.item(selected_item)['values']
        receita_id = meal_data[0]
        mostrar_detalhes_receita(receita_id, plano)
    else:
        messagebox.showwarning("Atenção", "Por favor selecione uma receita para obter detalhes.")

def mostrar_detalhes_receita(receita_id, plano):
    for widget in root.winfo_children():
        widget.destroy()
    
    #cria um frame principal com scrollbar
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    detalhes = obterDetalhesReceita(receita_id, API_KEY)
    if not detalhes:
        messagebox.showerror("Erro", "Detalhes da receita não disponíveis.")
        mostrar_menu_inicial()
        return
   
    tk.Label(scroll_frame, text=detalhes['title'], font=("Helvetica", 16)).pack(pady=10)
    tk.Label(scroll_frame, text=f"Tempo de preparo: {detalhes.get('readyInMinutes', 'N/A')} min").pack()
    tk.Label(scroll_frame, text=f"Doses: {detalhes.get('servings', 'N/A')}").pack()
    
    #exibir valores nutricionais 
    nutricion_data = detalhes.get('nutrition', {})
    if nutricion_data:
        calorias, proteinas, gorduras, hidratos = valoresNutricionais(nutricion_data)
        tk.Label(scroll_frame, text=f"Valores Nutricionais: {calorias} kcal | {proteinas} proteina | {gorduras} gordura | {hidratos} hidratos").pack(pady=5)
    else:
        tk.Label(scroll_frame, text="Informação nutricional não disponível.").pack(pady=5)
    
    #exibir os ingredientes necessarios para a realizacao da receita
    ingredientes_frame = tk.LabelFrame(scroll_frame, text="Ingredientes necessários", font=("Helvetica", 12, "bold"), padx=10, pady=10)
    ingredientes_frame.pack(padx=20, pady=10, fill="x")
    for ing in detalhes.get('extendedIngredients', []):
        tk.Label(ingredientes_frame, text=f" - {ing['name']}").pack(anchor="w")
    
    #modo preparo
    modo_preparo = obterModoPreparo(receita_id, API_KEY)
    if modo_preparo:
        tk.Label(scroll_frame, text="Modo de Preparo:", font=("Helvetica", 12, "bold")).pack(pady=5)
        for instrucao in modo_preparo:
            for passo in instrucao.get('steps', []):
                frame_passo = tk.Frame(scroll_frame)
                frame_passo.pack(anchor="w", padx=20, pady=2)

                #numero da etapa e texto em negrito
                tk.Label(frame_passo, text=f"Etapa {passo['number']}:", font=("Helvetica", 10, "bold")).pack(side="left")
                tk.Label(frame_passo, text=f" {passo['step']}", wraplength=700, justify="left").pack(side="left")
    else:
        tk.Label(scroll_frame, text="Modo de preparo não disponível.").pack()

    #comentarios
    tk.Label(scroll_frame, text="Comentários:", font=("Helvetica", 12, "bold")).pack(pady=5)
    try:
        with open('comentarios.json', 'r', encoding='utf-8') as f:
            comentarios = json.load(f).get(str(receita_id), [])
    except:
        comentarios = []
    if comentarios:
        for c in comentarios:
            tk.Label(scroll_frame, text=f" - {c['utilizador']}: {c['comentario']}").pack(anchor="w", padx=20)
    else:
        tk.Label(scroll_frame, text="Ainda não existem comentários sobre esta receita.").pack()

    tk.Button(scroll_frame, text="Adicionar Comentário", command=lambda: abrir_formulario_comentario(receita_id, plano)).pack(pady=10)
    tk.Button(scroll_frame, text="Substituir Ingrediente", command=lambda: abrir_formulario_substituicao(receita_id)).pack(pady=5)
    tk.Button(scroll_frame, text="Voltar para Refeições", command=lambda: mostrar_resultados(plano)).pack(pady=10)

def abrir_formulario_comentario(receita_id, plano):
    nova_janela = tk.Toplevel(root)
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
            guardarComentario(receita_id, comentario, nome)
            messagebox.showinfo("Sucesso", "Comentário guardado com sucesso.")
            nova_janela.destroy()
            mostrar_detalhes_receita(receita_id, plano)
        else:
            messagebox.showwarning("Campos obrigatórios", "Por favor, preencha o nome e adicione um comentário.")
    
    tk.Button(nova_janela, text="Guardar", command=guardar).grid(row=2, column=0, columnspan=2, pady=10)

def abrir_formulario_substituicao(receita_id):
    nova_janela = tk.Toplevel(root)
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
        
        #exemplo de substituicoes estaticas
        substituicoes = {
            "leite" : ["leite de soja", "leite de amendoa", "leite de aveia"],
            "ovo" : ["linhaça moida", "banana amassada", "pure de maça"],
            "farinha de trigo" : ["farinha de aveia", "farinha de arroz", "farinha de milho"],
            "açucar" : ["mel", "adocente", "xarope de agave"],
            "manteiga" : ["oleo de coco", "pure de abacate", "iogurte grego"]
        }

        sugestoes = substituicoes.get(ingrediente)
        sugestoes_text.delete("1.0", tk.END)
        if sugestoes:
            sugestoes_text.insert(tk.END, f"Substituições para '{ingrediente}':\n")
            for s in sugestoes:
                sugestoes_text.insert(tk.END, f" - {s}\n")
        else:
            sugestoes_text.insert(tk.END, f"Nenhuma sugestão disponível para '{ingrediente}'.")
    tk.Button(nova_janela, text="Sugerir Substituições", command=sugerir).grid(row=1, column=0, columnspan=2, pady=10)
    
#mostrar o menu princial
mostrar_menu_inicial()

#executar a interface
root.mainloop()

