"""Aplica as regras de transformação aos lotes e reúne os contadores."""

from etl.regras_transformacao import (
    calcular_valores_pedido,
    converter_data,
    converter_valor_monetario,
    padronizar_estados,
    remover_pedidos_duplicados,
    tratar_emails_nulos,
)


##transformar_clientes()	Aplica A1, A2 e A3
def transformar_clientes(clientes):
    """
    Aplica as regras A1, A2 e A3 aos clientes extraídos.

    Retorna:
        clientes_transformados: lista pronta para a carga
        contadores: resumo das transformações realizadas
    """

    # A1: preserva os e-mails nulos e contabiliza quantos existem.
    clientes, emails_nulos = tratar_emails_nulos(clientes)

    # A2: padroniza as siglas dos estados.
    clientes, estados_alterados = padronizar_estados(clientes)

    # Cria uma lista para armazenar os clientes com datas convertidas.
    clientes_transformados = []

    # A3: converte a data de cadastro de cada cliente.
    for cliente in clientes:

        # Copia o registro para preservar os dados de entrada.
        cliente_transformado = cliente.copy()

        # Converte a data para o tipo date do Python.
        cliente_transformado["cadastro_em"] = converter_data(
            cliente["cadastro_em"]
        )

        clientes_transformados.append(cliente_transformado)

    # Organiza os indicadores para os logs do ETL.
    contadores = {
        "clientes_processados": len(clientes_transformados),
        "emails_nulos": emails_nulos,
        "estados_padronizados": estados_alterados,
        "datas_convertidas": len(clientes_transformados)
    }

    return clientes_transformados, contadores

##transformar_pedidos()	Aplica A5, A6 e A3
def transformar_pedidos(pedidos):
    """
    Remove duplicatas, converte datas e calcula os valores dos pedidos.

    Retorna:
        pedidos_transformados: pedidos únicos e transformados
        contadores: resumo das operações
    """

    # A5: remove IDs repetidos, mantendo a primeira ocorrência.
    pedidos_unicos, duplicados = remover_pedidos_duplicados(pedidos)

    pedidos_transformados = []
    divergentes = 0

    # Processa cada pedido único.
    for pedido in pedidos_unicos:

        # A6: calcula valor_itens e identifica divergências.
        pedido_transformado = calcular_valores_pedido(pedido)

        # A3: converte a data do pedido.
        pedido_transformado["data_pedido"] = converter_data(
            pedido["data_pedido"]
        )

        # Conta os pedidos com valores divergentes.
        if pedido_transformado["divergente"]:
            divergentes += 1

        pedidos_transformados.append(pedido_transformado)

    # Organiza os indicadores para os logs do ETL.
    contadores = {
        "pedidos_brutos": len(pedidos),
        "pedidos_unicos": len(pedidos_transformados),
        "duplicados_descartados": duplicados,
        "pedidos_divergentes": divergentes,
        "datas_convertidas": len(pedidos_transformados),
    }

    return pedidos_transformados, contadores

##transformar_produtos()	Converte IDs e preços dos produtos
def transformar_produtos(produtos):
    """
    Converte os tipos dos produtos para a carga no PostgreSQL.

    Retorna:
        produtos_transformados: lista de produtos preparados
        contadores: resumo da transformação
    """

    # Lista que receberá os produtos transformados.
    produtos_transformados = []

    # Percorre os produtos extraídos do CSV.
    for produto in produtos:

        # Cria uma cópia para preservar os dados originais.
        produto_transformado = produto.copy()

        # Converte o identificador de texto para inteiro.
        produto_transformado["produto_id"] = int(
            produto["produto_id"]
        )

        # Converte o preço para Decimal com duas casas.
        produto_transformado["preco_base"] = converter_valor_monetario(
            produto["preco_base"]
        )

        # Adiciona o produto preparado à nova lista.
        produtos_transformados.append(produto_transformado)

    # Registra a quantidade processada.
    contadores = {
        "produtos_processados": len(produtos_transformados),
        "precos_convertidos": len(produtos_transformados)
    }

    return produtos_transformados, contadores

##transformar_itens_pedido()
def transformar_itens_pedido(pedidos):
    """
    Separa os itens dos pedidos em registros individuais,
    preparando-os para a tabela itens_pedido.

    Retorna:
        itens_transformados: lista de itens preparados
        contadores: quantidade de itens processados
    """

    # Lista que armazenará todos os itens.
    itens_transformados = []

    # Percorre os pedidos já deduplicados.
    for pedido in pedidos:

        # Identifica o pedido ao qual os itens pertencem.
        pedido_id = int(pedido["id"])

        # enumerate(..., start=1) numera os itens de cada pedido.
        for linha, item in enumerate(pedido["itens"], start=1):

            # Monta um registro com os campos exigidos pelo banco.
            item_transformado = {
                "pedido_id": pedido_id,
                "linha": linha,
                "produto_id": int(item["produto_id"]),
                "quantidade": int(item["quantidade"]),
                "preco_unitario": converter_valor_monetario(
                    item["preco_unitario"]
                )
            }

            # Adiciona o item à lista.
            itens_transformados.append(item_transformado)

    # Contador para os logs do ETL.
    contadores = {
        "itens_processados": len(itens_transformados)
    }

    return itens_transformados, contadores