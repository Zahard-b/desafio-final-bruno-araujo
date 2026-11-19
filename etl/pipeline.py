import json
import getpass
import psycopg2
from etl.relatorio_qualidade import gerar_relatorio_qualidade

from etl.extracao import ler_produtos_csv
from etl.transformacao import (
    transformar_clientes,
    transformar_produtos,
    transformar_pedidos,
    transformar_itens_pedido
)
from etl.carga import (
    carregar_clientes,
    carregar_produtos,
    carregar_pedidos,
    carregar_itens_pedido
)


def executar_pipeline():
    # ETAPA 1: LEITURA DOS DADOS BRUTOS
    # Carrega os arquivos preservados pela extração da API e do CSV.
    with open("brutos/clientes.json", encoding="utf-8") as arquivo:
        clientes_brutos = json.load(arquivo)

    with open("brutos/pedidos.json", encoding="utf-8") as arquivo:
        pedidos_brutos = json.load(arquivo)

    produtos_brutos = ler_produtos_csv("brutos/produtos.csv")

    print("Leitura dos dados brutos concluída.")

    # ETAPA 2: TRANSFORMAÇÃO
    clientes, metricas_clientes = transformar_clientes(clientes_brutos)
    produtos, metricas_produtos = transformar_produtos(produtos_brutos)
    pedidos, metricas_pedidos = transformar_pedidos(pedidos_brutos)

    # Gera os itens a partir dos pedidos sem duplicatas.
    itens, metricas_itens = transformar_itens_pedido(pedidos)

    print("Transformação concluída.")

    # ETAPA 3: CARGA
    # Solicita a senha sem mostrá-la no terminal.
    senha = getpass.getpass("Senha do PostgreSQL: ")

    conexao = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="verdejar",
        user="postgres",
        password=senha,
        options="-c lc_messages=C"
    )

    try:
        # Carrega na ordem correta para respeitar as chaves estrangeiras.
        total_produtos = carregar_produtos(conexao, produtos)
        total_clientes = carregar_clientes(conexao, clientes)
        total_pedidos = carregar_pedidos(conexao, pedidos)
        total_itens = carregar_itens_pedido(conexao, itens)

        # Confirma todas as alterações somente após as quatro cargas.
        conexao.commit()

        print("Carga concluída com sucesso!")
        print("Produtos carregados:", total_produtos)
        print("Clientes carregados:", total_clientes)
        print("Pedidos carregados:", total_pedidos)
        print("Itens carregados:", total_itens)

        # Exibe as métricas das transformações.
        print("E-mails nulos:", metricas_clientes["emails_nulos"])
        print("Estados padronizados:", metricas_clientes["estados_padronizados"])
        print("Duplicados descartados:", metricas_pedidos["duplicados_descartados"])
        print("Pedidos divergentes:", metricas_pedidos["pedidos_divergentes"])

    except Exception:
        # Se alguma carga falhar, desfaz todas as alterações da transação.
        conexao.rollback()
        print("ERRO: carga cancelada. ROLLBACK executado.")
        raise

    finally:
        # Fecha a conexão mesmo quando ocorre algum erro.
        conexao.close()

    # ETAPA 4: RELATÓRIO DE QUALIDADE (STRETCH)
    # Reúne os contadores das seis regras de transformação.
    metricas_qualidade = {
        "emails_nulos": metricas_clientes["emails_nulos"],
        "estados_padronizados": metricas_clientes["estados_padronizados"],

        # A3: datas convertidas de clientes e pedidos únicos.
        "datas_convertidas": (
            metricas_clientes["datas_convertidas"]
            + metricas_pedidos["datas_convertidas"]
        ),

        # A4: campos monetários preparados para carga.
        "valores_convertidos": (
            metricas_produtos["precos_convertidos"]
            + metricas_pedidos["pedidos_unicos"]
            + metricas_itens["itens_processados"]
        ),

        "duplicados_descartados": metricas_pedidos["duplicados_descartados"],
        "pedidos_divergentes": metricas_pedidos["pedidos_divergentes"]
    }

    # Gera o relatório somente após uma carga concluída com sucesso.
    gerar_relatorio_qualidade(metricas_qualidade)


if __name__ == "__main__":
    executar_pipeline()

