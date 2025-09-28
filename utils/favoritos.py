"""
Modulo utilitario para gerir receitas favoritas.
Permite adicionar, remover e verificar favoritos. os favoritos sao guardados num ficheiro json
"""

import os 
import json

#caminho para o ficheiro de favoritos
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_favoritos = os.path.join(base_path, "..", "data", "favoritos.json")

def carregar_favoritos():
    try:
        with open(caminho_favoritos, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except(FileNotFoundError, json.JSONDecodeError):
        return set()

def guardar_favoritos(favoritos):
    with open(caminho_favoritos, "w", encoding="utf-8") as f:
        json.dump(list(favoritos), f, indent=4, ensure_ascii=False)

def adicionar_favorito(receita_id):
    favoritos = carregar_favoritos()
    favoritos.add(str(receita_id))
    guardar_favoritos(favoritos)

def remover_favorito(receita_id):
    favoritos = carregar_favoritos()
    favoritos.discard(str(receita_id))
    guardar_favoritos(favoritos)

def is_favorito(receita_id):
    favoritos = carregar_favoritos()
    return str(receita_id) in favoritos