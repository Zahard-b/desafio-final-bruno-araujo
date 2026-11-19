# Importa a biblioteca responsável pelas requisições HTTP
import requests
import json
import csv
from pathlib import Path
import shutil


def extrair_paginado(url_base, rota, tamanho_pagina=50):
    """
    Extrai todos os registros de uma rota paginada da API.

    Parâmetros:
        url_base: endereço principal da API.
        rota: rota consultada, como "/clientes" ou "/pedidos".
        tamanho_pagina: quantidade de registros solicitados por página.

    Retorna:
        Lista com todos os registros extraídos.
        None se ocorrer algum erro durante a extração.
    """

    registros = []
    pagina = 1

    # Monta o endereço da rota, evitando barras duplicadas.
    url = f"{url_base.rstrip('/')}/{rota.lstrip('/')}"

    while True:

        # ETAPA 1: Consultar a página atual.
        try:
            resposta = requests.get(
                url,
                params={
                    "page": pagina,
                    "page_size": tamanho_pagina
                },
                timeout=10
            )

            # Interrompe a extração se a API retornar erro HTTP.
            resposta.raise_for_status()

            # Converte a resposta JSON em dados Python.
            dados = resposta.json()

        except requests.exceptions.HTTPError as erro:
            print(f"Erro HTTP na página {pagina}: {erro}")
            return None

        except requests.exceptions.RequestException as erro:
            print(f"Erro de conexão na página {pagina}: {erro}")
            return None

        except ValueError as erro:
            print(f"JSON inválido na página {pagina}: {erro}")
            return None

        # ETAPA 2: Validar a estrutura da resposta.
        if not isinstance(dados, dict):
            print(f"Erro na página {pagina}: resposta JSON não é um objeto.")
            return None

        if "items" not in dados or "total_pages" not in dados:
            print(
                f"Erro na página {pagina}: "
                "JSON sem os campos obrigatórios 'items' e 'total_pages'."
            )
            return None

        if not isinstance(dados["items"], list):
            print(f"Erro na página {pagina}: 'items' não é uma lista.")
            return None

        if (
            not isinstance(dados["total_pages"], int)
            or isinstance(dados["total_pages"], bool)
            or dados["total_pages"] < pagina
        ):
            print(f"Erro na página {pagina}: 'total_pages' inválido.")
            return None

        # ETAPA 3: Armazenar os registros extraídos.
        itens = dados["items"]

        registros.extend(itens)

        print(f"Página {pagina} extraída: {len(itens)} registros")

        # ETAPA 4: Verificar se ainda existem páginas.
        if pagina >= dados["total_pages"]:
            break

        pagina += 1

    print(f"Extração concluída: {len(registros)} registros")

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

def executar_extracao():
    """
    Executa a extração completa dos dados da Verdejar.

    Consulta as APIs de clientes e pedidos e preserva os
    registros originais na pasta brutos, junto ao CSV de produtos.
    """

    # Configuração da API local.
    url_base = "http://127.0.0.1:8000"

    # Identifica a pasta principal do projeto.
    raiz_projeto = Path(__file__).resolve().parent.parent

    # Define onde os arquivos serão armazenados.
    pasta_brutos = raiz_projeto / "brutos"

    # Localiza o CSV original fornecido no desafio.
    csv_origem = raiz_projeto / "insumos" / "dados" / "produtos.csv"
    csv_destino = pasta_brutos / "produtos.csv"

    print("Iniciando extração dos dados...")

    # ETAPA 1: Extrair todos os clientes.
    clientes = extrair_paginado(url_base, "/clientes")

    if clientes is None:
        print("Erro: não foi possível extrair os clientes.")
        return

    # ETAPA 2: Extrair todos os pedidos.
    pedidos = extrair_paginado(url_base, "/pedidos")

    if pedidos is None:
        print("Erro: não foi possível extrair os pedidos.")
        return

    # ETAPA 3: Verificar se o CSV original existe.
    if not csv_origem.is_file():
        print(f"Erro: CSV de produtos não encontrado em {csv_origem}")
        return

    # ETAPA 4: Criar a pasta de destino, se necessário.
    pasta_brutos.mkdir(parents=True, exist_ok=True)

    # ETAPA 5: Preservar os dados brutos.
    salvar_json(clientes, pasta_brutos / "clientes.json")
    salvar_json(pedidos, pasta_brutos / "pedidos.json")

    # Copia o CSV original sem transformar seus valores.
    shutil.copyfile(csv_origem, csv_destino)

    # Exibe o resumo da extração.
    print("Extração finalizada com sucesso!")
    print("Clientes extraídos:", len(clientes))
    print("Pedidos extraídos:", len(pedidos))
    print("Produtos extraídos:", len(ler_produtos_csv(csv_destino)))


# Executa a função quando o arquivo é iniciado pelo terminal.
if __name__ == "__main__":
    executar_extracao()