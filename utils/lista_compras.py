""" 
Modulo de gestao das listas de compras da aplicacao
Permite inicializar o ficheiro de armazenamento, guardar novas listas e obter todas as listas guardadas anteriormente
"""
import os
import json

#caminhos base para a pasta data e ficheiro de lista de compras
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_pasta_data = os.path.join(base_path, "..", "data")
caminho_lista_compras = os.path.join(caminho_pasta_data, "lista_compras.json")

#Garante que a pasta data e o ficheiro lista_compras.json existem e caso nao existem cria-os
def inicializarFicheiroCompras():
    if not os.path.exists(caminho_pasta_data):
        os.makedirs(caminho_pasta_data)
    if not os.path.exists(caminho_lista_compras):
        with open(caminho_lista_compras, 'w', encoding='utf-8') as f:
            json.dump({}, f)

#Guarda uma nova lista de compras associada a um identificador(data e hora)
def guardarListaCompras(lista, identificador):
    try:
        with open(caminho_lista_compras, 'r', encoding='utf-8') as f:
            listas = json.load(f)
    except(FileNotFoundError, json.JSONDecodeError):
        listas = {}
    
    listas[identificador] = lista

    with open(caminho_lista_compras, 'w', encoding='utf-8') as f:
        json.dump(listas, f, indent=4, ensure_ascii=False)

#Devolve todas as listas de compras que foram guardadas
def obterListasComprasGuardadas():
    try:
        with open(caminho_lista_compras, 'r', encoding='utf-8') as f:
            return json.load(f)
    except(FileNotFoundError, json.JSONDecodeError):
        return {}