# Importa a biblioteca responsável pelas requisições HTTP
import requests
import json
import csv


# Função reutilizável para extrair registros de uma API paginada
def extrair_paginado(url_base, rota, tamanho_pagina=50):

    # Lista que armazenará os registros extraídos de todas as páginas
    registros = []

    # Define a primeira página a ser consultada
    pagina = 1

    # Repete a extração até alcançar a última página
    while True:

        # Tenta realizar a requisição e interpretar a resposta
        try:

            # Monta a URL e consulta a página atual da API
            resposta = requests.get(
                f"{url_base.rstrip('/')}/{rota.lstrip('/')}",

                # Parâmetros enviados para controlar a paginação
                params={
                    "page": pagina,
                    "page_size": tamanho_pagina
                },

                # Tempo máximo de espera pela resposta, em segundos
                timeout=10
            )

            # Verifica se a resposta contém algum erro HTTP
            # Exemplos: 404 (não encontrado) e 500 (erro interno)
            resposta.raise_for_status()

            # Converte a resposta JSON em um dicionário Python
            dados = resposta.json()

        # Trata erros HTTP retornados pela API
        except requests.exceptions.HTTPError as erro:
            print(f"Erro HTTP na página {pagina}: {erro}")
            return None

        # Trata erros de conexão e tempo de espera esgotado
        except requests.exceptions.RequestException as erro:
            print(f"Erro de conexão na página {pagina}: {erro}")
            return None

        # Trata respostas que não possuem JSON válido
        except ValueError as erro:
            print(f"JSON inválido na página {pagina}: {erro}")
            return None

        # Adiciona os registros da página atual à lista principal
        registros.extend(dados["items"])

        # Mostra quantos registros foram extraídos da página
        print(
            f"Página {pagina} extraída: "
            f"{len(dados['items'])} registros"
        )

        # Verifica se a página atual é a última disponível
        if pagina >= dados["total_pages"]:

            # Encerra o laço quando todas as páginas forem extraídas
            break

        # Incrementa o número para consultar a próxima página
        pagina += 1

    # Exibe a quantidade total de registros extraídos
    print(f"Extração concluída: {len(registros)} registros")

    # Devolve todos os registros para as próximas etapas do ETL
    return registros

def salvar_json(registros, caminho_arquivo):
    """
    Salva os registros extraídos da API em um arquivo JSON,
    preservando os dados antes das transformações.
    """

    # Abre ou cria o arquivo no caminho informado.
    # O modo "w" permite escrever e substituir seu conteúdo.
    # encoding="utf-8" permite armazenar caracteres acentuados.
    with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:

        # Converte a lista de registros Python para JSON.
        # ensure_ascii=False preserva acentos.
        # indent=4 organiza o conteúdo para facilitar a leitura.
        json.dump(registros, arquivo, ensure_ascii=False, indent=4)

    # Confirma que o arquivo foi salvo.
    print(f"Dados brutos salvos em: {caminho_arquivo}")

def ler_produtos_csv(caminho_arquivo):
    """
    Lê o arquivo CSV de produtos e devolve
    uma lista de dicionários com seus registros.
    """

    # Lista que armazenará os produtos encontrados no CSV
    produtos = []

    # Abre o arquivo para leitura
    with open(caminho_arquivo, "r", encoding="utf-8-sig", newline="") as arquivo:

        # Lê o cabeçalho do CSV e usa os nomes das colunas como chaves
        leitor = csv.DictReader(arquivo)

        # Percorre cada linha do arquivo
        for linha in leitor:

            # Adiciona o produto à lista sem transformar seus valores
            produtos.append(linha)

    # Mostra a quantidade de produtos encontrados
    print(f"Produtos extraídos do CSV: {len(produtos)}")

    # Devolve a lista para as próximas etapas do ETL
    return produtos