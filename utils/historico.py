"""
Modulo para a gestao do historico de planos de refeicoes
permite guardar e consultar planos de refeicoes previamente criados
"""

import os
import json
from datetime import datetime

#caminho absoluto para o ficheiro de historico na pasta "data"
base_dir = os.path.dirname(os.path.abspath(__file__))  #caminho da pasta /utils
projeto_dir = os.path.dirname(base_dir) #volta à pasta principal
caminho_ficheiro = os.path.join(projeto_dir, "data", "historico.json")

#Guarda um plano de refeicoes no historico local, acrescenta nova entrada com data, dieta, calorias e lista de refeicoes
def guardarPlanoHistorico(plano, dieta, calorias):
    try:
        if os.path.exists(caminho_ficheiro):
            with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        else:
            historico = []
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []

    #extrai refeições conforme o tipo de plano
    refeicoes = []
    if "meals" in plano and plano["meals"]:
        #plano diario
        for meal in plano["meals"]:
            refeicoes.append({"id": meal.get("id"), "title": meal.get("title"), "readyInMinutes": meal.get("readyInMinutes"), "servings": meal.get("servings")})
    elif "week" in plano:
        #plano semanal
        for dia, info in plano["week"].items():
            meals = info.get("meals", [])
            for meal in meals:
                refeicoes.append({"dia": dia, "id": meal.get("id"), "title": meal.get("title"), "readyInMinutes": meal.get("readyInMinutes"), "servings": meal.get("servings")})
    else:
        print("Erro: Nenhuma refeição encontrada no plano.")
        return
    
    if not refeicoes:
        print("Erro: Nenhuma refeição encontrada no plano.")
        return
    
    #cria o novo registo de plano a adicionar no historico
    novo_plano = {
        "data":datetime.now().strftime("%Y-%m-%d %H:%M"),
        "dieta": dieta if dieta else "Nenhuma",
        "calorias": calorias if calorias else "Não definido",
        "refeicoes": refeicoes
    }
    historico.append(novo_plano)

    #guardar o historico atualizado no ficheiro
    with open(caminho_ficheiro, 'w', encoding='utf-8') as f:
            json.dump(historico, f, indent=4, ensure_ascii=False)

#Carrega e retorna a lista de planos guardados no historico
def mostrarHistorico():
    try:
        with open(caminho_ficheiro, 'r', encoding='utf-8') as f:
            return json.load(f)
    except(FileNotFoundError, json.JSONDecodeError):
        return []
    