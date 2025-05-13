import requests

#gera um plano de refeicoes utilizando a API sPOONACULAR
#obtem um plano de refeicoes com base nas preferencia do utilizador
def planoRefeicoes(api_key, time_frame = 'day', target_calories = None, dieta = None, excluir = None):
    url = "https://api.spoonacular.com/mealplanner/generate"  #endpoint da API
    params = {
        "timeFrame": time_frame,
        "apiKey": api_key
    }
    #adiciona parametros opcionais
    if target_calories:
        params["targetCalories"] = target_calories
    if dieta:
        params["diet"] = dieta
    if excluir:
        params["exclude"] = excluir
    #faz a requisicao para a API
    response = requests.get(url, params=params)
    if response.status_code == 200:
        #retorna o plano de refeicao em JSON
        return response.json()                                                      
    else:
        #em caso de erro, exibe uma mensagem e retorna None
        print(f"Erro ao gerar plano de refeições: {response.status_code}, {response.text}")
        return None

#pesquisa receitas baseadas nos ingredientes disponiveis
# obtem receitas que podem ser feitas com os ingredientes fornecidos    
def obterReceitas(ingredientes, api_key, numero_receitas = 5, dieta = None, intolerancias = None):
    url = "https://api.spoonacular.com/recipes/complexSearch"
    params = { 
        "includeIngredients": ",".join(ingredientes) ,
        "number": numero_receitas,
        "ranking": 1, #priorizar receitas que usam mais os ingredientes disponiveis
        "ignorePantry": True, #ignora items tipos  da despensa(sal, agua, etc)
        "apiKey": api_key
    }
    #adiciona parametros opcionais
    if dieta:
        params["diet"] = dieta
    if intolerancias:
        params['intolerances'] = ",".join(intolerancias)

    response = requests.get(url, params=params)
    if response.status_code == 200:
        #retorna a lista de receitas em JSON
        return response.json().get('results', []) 
    else:
        print("Erro ao obter receitas: ", response.status_code, response.text)
        return[]

#obtem informacoes detalhadas acerca de uma receita especifica, como ingredientes e valores nutricionais
def obterDetalhesReceita(receita_id, api_key):
    url = f"https://api.spoonacular.com/recipes/{receita_id}/information"
    params = {
        "includeNutrition":True, #inclui informacoes nutricionais detalhadas
        "apiKey": api_key
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao obter detalhes da receita {receita_id}: ", response.status_code, response.text)
        return {}

#extrai os valores nutricionais principais(calorias, proteinas, gorduras, hidratos)   
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

#obtem o passo-a-passo do modo de preparo da receita
def obterModoPreparo(receita_id, api_key):
    url = f"https://api.spoonacular.com/recipes/{receita_id}/analyzedInstructions"
    params = {
        "apiKey":api_key,
        "stepBreakdown": True #divide ainda mais as etapas da receita
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro ao obter o modo de preparo da receita {receita_id}: ", response.status_code, response.text)
        return []

#sugere substitutos para um ingrediente 
def substituicaoIngrediente(nome_ingrediente, api_key):
    url = "https://api.spoonacular.com/food/ingredients/substitutes" 
    params = {
        "ingredientName": nome_ingrediente,
        "apiKey": api_key
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        dados = response.json()
        if "substitutes" in dados:
            return dados["substitutes"]
        else:
            print(f"\nNão há substitutos disponiveis para {nome_ingrediente}.")
            return []
    else:
        print(f"Erro ao obter substitutos para {nome_ingrediente}: ", response.status_code, response.text)
        return []
    
#obtem lista de compras para o plano gerado
def obterListaCompras(meals, api_key):
    lista_ingredientes = {}
    print("\nA gerar lista de compras de acordo com as receitas fornecidas.")

    for refeicao in meals:
        detalhes = obterDetalhesReceita(refeicao['id'], api_key)
        if detalhes:
            for ingrediente in detalhes.get("extendedIngredients", []):
                nome = ingrediente['name']
                medidas_metric = ingrediente.get('measures', {}).get('metric', {})
                quantidade = medidas_metric.get('amount', 0)

                if nome in lista_ingredientes:
                    lista_ingredientes[nome]['quantidade'] += quantidade
                else:
                    lista_ingredientes[nome] = {
                        'quantidade': quantidade,
                    }
    print("\nLista de compras necessarias para o seu plano:")
    for nome, info in lista_ingredientes.items():
        print(f" - {nome}: {round(info['quantidade'], 2)}")
