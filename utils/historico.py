import json
from datetime import datetime
import os

def guardarPlanoHistorico(plano, dieta, calorias):
    local_arquivo = "historico.json"

    try:
        if os.path.exists(local_arquivo):
            with open(local_arquivo, 'r', encoding='utf-8') as f:
                historico = json.load(f)
        else:
            historico = []
    except (FileNotFoundError, json.JSONDecodeError):
        historico = []
    
    novo_plano = {
        "data":datetime.now().strftime("%Y-%m-%D %H:%M"),
        "dieta": dieta if dieta else "Nenhuma",
        "calorias": calorias if calorias else "Não definido",
        "refeicoes": [meal['title'] for meal in plano["meals"]]
    }
    historico.append(novo_plano)

    with open(local_arquivo, 'w', encoding='utf-8') as f:
        json.dump(historico, f, indent=4, ensure_ascii=False)
    print("\nPlano guardado no histórico com sucesso.")

def mostrarHistorico():
    try:
        with open('historico.json', 'r', encoding='utf-8') as f:
            historico = json.load(f)
        return historico
    except(FileNotFoundError, json.JSONDecodeError):
        return []
    