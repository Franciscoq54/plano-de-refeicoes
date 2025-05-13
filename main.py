from api.api_requests import planoRefeicoes, obterDetalhesReceita, obterModoPreparo, substituicaoIngrediente, obterListaCompras 
from utils.comentarios import guardarComentario, mostrarComentarios
from utils.historico import guardarPlanoHistorico, mostrarHistorico
from utils.nutricionais import valoresNutricionais

def main():
    #escolha de dieta
    print("Bem vindo ao Planeador de Refeições:")
    ver_historico = input("Deseja consultar planos anteriores guardados? (sim/nao): ").strip().lower()
    if ver_historico == "sim":
        mostrarHistorico()
        
    print("\nOpções de dieta disponíveis: ")
    print("- vegetarian\n- vegan\n- gluten free\n- ketogenic\n- pescetarian\n- paleo\n- etc...\n")
    dieta = input("Qual o tipo de dieta que deseja seguir: ").strip().lower()
    if dieta == "":
        dieta = None
    #ingredientes disponiveis
    ingredientes = [i.strip() for i in input("Que ingredientes tem disponivel no momento(separados por virgulas): ").strip().split(",")]
    #intolerencias alimentares 
    intolerancias_input = input("Tem alguma intolerencia alimentar(separar por virgulas): ").strip().lower()
    intolerencias = [i.strip() for i in intolerancias_input.split(",")] if intolerancias_input else None
  

    api_key = "5c6f3108b2c34e5d9eb78b8b82a1e4e6"
  
   
    print("\nSerá gerado um plano de refeições personalizado de acordo com as suas perferencias:")
    
    while True:
        time_frame = input("Qual o período do plano?(dia/semana): ").strip().lower()   
        if time_frame in ["dia", "semana"]:
             break
        else:
                print("Entrada inválida. Escreva 'dia' ou 'semana'.")

    target_calories_input = input("Qual a meta de calorias para o plano?").strip()
    target_calories = None
    if target_calories_input:
        try:
            target_calories = int(target_calories_input)
        except ValueError:
            print("Valor de calorias inserido é invalido.")
            target_calories = None
    #gera o plano de refeições
    plano = planoRefeicoes(api_key, time_frame=time_frame, target_calories=target_calories, dieta=dieta, excluir=",".join(intolerencias) if intolerencias else None)

    if plano:
        guardarPlanoHistorico(plano, dieta, target_calories)
        meals = plano.get('meals', [])
        if meals:
            print("\nO teu plano de refeições já está disponível. Aqui estão as refeições:")
            for i, refeicao in enumerate(meals, 1):
                print(f"{i}. {refeicao['title']} (Doses: {refeicao['servings']}, Tempo de preparo: {refeicao['readyInMinutes']} minutos)")
            while True:
                try:
                    escolha = int(input("\nIndique o número da receita do plano que deseja consultar detalhadamente:"))
                    if 1 <= escolha <= len(meals):
                        #escolha é valida, sai do loop
                        break
                    else:
                        print("Por favor, insira um número válido dentro do intervalo das receitas disponíveis. ")
                except ValueError:
                    print("Entrada inválida. Por favor, insira um número.")
            refeicao_escolhida = meals[int(escolha) - 1]
            
            detalhes = obterDetalhesReceita(refeicao_escolhida['id'], api_key)
            if detalhes:
                calorias, proteinas, gorduras, hidratos = valoresNutricionais(detalhes.get('nutrition', {}))
                ingredientes_usados = [ingrediente['name'] for ingrediente in detalhes.get('extendedIngredients', [])]
                    
                print(f"\n{detalhes['title']}")
                print(f"Tempo de preparo: {detalhes.get('readyInMinutes', 'N/A')} min")
                print(f"Número de doses: {detalhes.get('servings', 'N/A')}")
                print(f"\nIngredientes necessários para {detalhes['title']}:")
                for ing in ingredientes_usados:
                    print(f" - {ing}")
                print(f"\nInformação Nutricional: {calorias} Kcal | {proteinas} proteína | {gorduras} gordura | {hidratos} hidratos")

                modo_preparo = obterModoPreparo(refeicao_escolhida['id'], api_key)
                if modo_preparo:
                    print("\nModo de preparação:")
                    for instrucao in modo_preparo:
                        for passo in instrucao.get('steps', []):
                            print(f"Etapa {passo['number']}: {passo['step']}")
                else:
                    print("\nModo de preparo não disponível.")

                mostrarComentarios(refeicao_escolhida['id'])
                adicionar_comentario = input("\nPretende adicionar um comentário sobre esta receita?(sim/nao): ").strip().lower()
                if adicionar_comentario == "sim":
                    nome_utilizador = input("Insira o nome de utilizador: ").strip()
                    comentario = input("Escreva o seu comentário: ").strip()
                    guardarComentario(refeicao_escolhida['id'], comentario, nome_utilizador)
                    print("Comentário guardado com sucesso.")
                    
                substituir = input("\nDeseja receber sugestões de substitutos para algum ingrediente desta receita?(sim/nao): ").lower()
                if substituir == "sim":
                    ingrediente_subtituir = input("Qual o ingrediente que deseja procurar por substitutos: ").strip()
                    substitutos = substituicaoIngrediente(ingrediente_subtituir, api_key)
                    if substitutos:
                        print(f"\nSubstitutos para {ingrediente_subtituir}: ")
                        for sub in substitutos:
                            print(f" - {sub}")
                    else:
                        print(f"\nInfelizmente, não foi possível encontrar substitutos para {ingrediente_subtituir}.")
                ver_lista = input(f"\nDeseja consultar a lista de compras que necessita? (sim/nao): ").strip().lower()
                if ver_lista == "sim":
                    obterListaCompras(meals, api_key)    
            else:
                print("Não foi possível obter os detalhes da receita.")
        else:
            print("Não há refeições disponiveis no plano. Tente ajustar as suas preferências e tente novamente.")
    else:
        print("Não foi possível criar o teu plano de refeições.")
   
#execucao do programa principal
if __name__ == "__main__":

    main()