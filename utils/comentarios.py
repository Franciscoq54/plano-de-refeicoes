import json

#guarda um comentario feito a uma receita no ficheiro json local
def guardarComentario(receita_id, comentario, nome_utilizador):
    try:
        with open('comentarios.json', 'r', encoding='utf-8') as f:
            comentarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comentarios = {}
    
    if str(receita_id) not in comentarios:
        comentarios[str(receita_id)] = []
    
    comentarios[str(receita_id)].append({
        "utilizador": nome_utilizador,
        "comentario": comentario
    })
    with open('comentarios.json', 'w', encoding = 'utf-8') as f:
        json.dump(comentarios, f, indent=4, ensure_ascii=False)

#exibe todos os comentarios associados a uma receita
def mostrarComentarios(receita_id):
    try:
        with open('comentarios.json', 'r', encoding='utf-8') as f:
            comentarios = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        comentarios = {}    
    if str(receita_id) in comentarios:
        print("\nComentários de utilizadores sobre esta receita:")
        for c in comentarios[str(receita_id)]:
            print(f"- {c['utilizador']}: {c['comentario']}")
    else:
        print("\nAinda não existem comentários para esta receita.")
