"""
Modulo de gestao de comentarios de utilizadores sobre receitas´
permite inicializar o ficheiro de guardar, ler e exibir comentarios associados a receita
"""
import os
import json

#caminho base para a pasta de dados(/data)
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_ficheiro = os.path.join(base_path, "..", "data")
caminho_comentarios = os.path.join(caminho_ficheiro, "comentarios.json")

#Garante a exixtencia da pasta e ficheiro de comentarios associados a receita
def inicializarFicheiros():
    if not os.path.exists(caminho_ficheiro):
        os.makedirs(caminho_ficheiro)

    if not os.path.exists(caminho_comentarios):
        with open(caminho_comentarios, 'w', encoding='utf-8') as f:
            json.dump({}, f)

#Le e devolve a lista de comentarios associados a uma receita
def lerComentarios(receita_id):
    try:
        with open(caminho_comentarios, 'r', encoding='utf-8') as f:
            comentarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comentarios = {}
    return comentarios.get(str(receita_id), [])

#guarda um novo comentario 
def guardarComentario(receita_id, comentario, nome_utilizador):
    try:
        with open(caminho_comentarios, 'r', encoding='utf-8') as f:
            comentarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comentarios = {}
    
    if str(receita_id) not in comentarios:
        comentarios[str(receita_id)] = []
    
    comentarios[str(receita_id)].append({
        "utilizador": nome_utilizador,
        "comentario": comentario
    })
    with open(caminho_comentarios, 'w', encoding = 'utf-8') as f:
        json.dump(comentarios, f, indent=4, ensure_ascii=False)

#Imprime todos os comentarios associados aquela receita 
def mostrarComentarios(receita_id):
    try:
        with open(caminho_comentarios, 'r', encoding='utf-8') as f:
            comentarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comentarios = {} 

    if str(receita_id) in comentarios:
        print("\nComentários de utilizadores sobre esta receita:")
        for c in comentarios[str(receita_id)]:
            print(f"- {c['utilizador']}: {c['comentario']}")
    else:
        print("\nAinda não existem comentários para esta receita.")
