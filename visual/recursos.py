"""
Fornece utilitarios para o carregamento e manipulação de imagens.
Usado para inserir banners, icones e outro tipo de elementos graficos na interface
"""

import os
from PIL import Image, ImageTk

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
RECURSOS_PATH = os.path.join(BASE_PATH, "recursos")

def caminho_recurso(nome_arquivo):
    return os.path.join(RECURSOS_PATH, nome_arquivo)

def carregar_imagem(nome_arquivo, tamanho=None):
    #carrega uma imagem da pasta recursos
    caminho = caminho_recurso(nome_arquivo)
    if not os.path.exists(caminho):
        print(f"[Aviso] Imagem não encontrada: {caminho}")
        return None
    img = Image.open(caminho)
    if tamanho:
        img = img.resize(tamanho)
    return ImageTk.PhotoImage(img)
