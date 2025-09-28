"""
Modulo utilitario para extraçao e formatação dos valores nutricionais 
"""

#Extrai os valores nutricionais principais(calorias, proteinas, gorduras e hidratos) a partir de um dicionario fornecido pela API
def valoresNutricionais(valNutricionais):
    calorias = proteinas = gorduras = hidratos = "N/A"

    if valNutricionais and 'nutrients' in valNutricionais:
        for item in valNutricionais['nutrients']:
            nome = item['name'].lower()
            if nome == "calories":
                calorias = f"{item['amount']} {item['unit']}"
            elif nome == "protein":
                proteinas = f"{item['amount']} {item['unit']}"
            elif nome == "fat":
                gorduras = f"{item['amount']} {item['unit']}"
            elif nome == "carbohydrates":
                hidratos = f"{item['amount']} {item['unit']}"
    return calorias, proteinas, gorduras, hidratos  