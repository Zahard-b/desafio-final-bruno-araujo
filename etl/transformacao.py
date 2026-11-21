"""
Transformações de dados do ETL Verdejar.

Este módulo contém:
- Regras A1–A6 de qualidade e padronização dos dados.
- Funções que aplicam essas regras aos registros extraídos.
- Preparação dos dados para carga no PostgreSQL.

As funções de transformação não realizam consultas à API
nem operações no banco de dados.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation


# ==========================================================
# REGRAS DE QUALIDADE DOS DADOS — A1 A A6
# ==========================================================

##A1

def tratar_emails_nulos(clientes):
    """
    Regra A1: identifica e contabiliza clientes sem e-mail.

    Clientes com e-mail nulo são preservados, pois esse campo
    não é obrigatório no contrato de dados.

    Retorna:
        - Lista original de clientes, sem alterações.
        - Quantidade de clientes com e-mail nulo ou ausente.
    """

    total_nulos = 0

    for cliente in clientes:
        # .get() também retorna None quando a chave não existe.
        if cliente.get("email") is None:
            total_nulos += 1

    return clientes, total_nulos

## A2

def padronizar_estados(clientes):
    """
    Regra A2: padroniza as siglas dos estados para maiúsculas.

    Preserva os registros originais, criando cópias dos clientes.

    Retorna:
        - Lista de clientes com estados padronizados.
        - Quantidade de estados que precisaram de alteração.
    """

    clientes_transformados = []
    total_alterados = 0

    for cliente in clientes:
        # Cria uma cópia para não modificar os dados originais.
        cliente_transformado = cliente.copy()

        estado_original = cliente_transformado["estado"]
        estado_padronizado = estado_original.upper()

        # Contabiliza apenas os estados que foram modificados.
        if estado_original != estado_padronizado:
            total_alterados += 1

        cliente_transformado["estado"] = estado_padronizado
        clientes_transformados.append(cliente_transformado)

    return clientes_transformados, total_alterados

## A3

def converter_data(valor):
    """
    Regra A3: converte datas em texto para o tipo date do Python.

    Formatos aceitos:
        - YYYY-MM-DD (exemplo: 2026-03-15)
        - DD/MM/YYYY (exemplo: 15/03/2026)

    Retorna:
        Objeto date com a data convertida.

    Lança ValueError quando a data é inválida ou não
    corresponde a nenhum dos formatos aceitos.
    """

    formatos = ("%Y-%m-%d", "%d/%m/%Y")

    # Tenta converter a data usando cada formato permitido.
    for formato in formatos:
        try:
            return datetime.strptime(valor, formato).date()
        except ValueError:
            continue

    # Impede que datas inválidas sejam enviadas ao banco.
    raise ValueError(f"Formato de data inválido: {valor}")

## A4

def converter_valor_monetario(valor):
    """
    Regra A4: converte valores monetários para Decimal.

    Aceita números e textos com ponto ou vírgula decimal.

    Exemplos:
        "125,50" -> Decimal("125.50")
        "125.50" -> Decimal("125.50")
        125      -> Decimal("125.00")

    Retorna:
        Decimal com duas casas decimais.

    Lança ValueError para valores inválidos.
    """

    try:
        # Normaliza o separador decimal.
        texto = str(valor).strip().replace(",", ".")

        # Decimal evita imprecisões comuns em cálculos com float.
        numero = Decimal(texto)

        # Impede valores especiais como NaN e Infinity.
        if not numero.is_finite():
            raise ValueError(f"Valor monetário inválido: {valor}")

        # Padroniza o resultado com duas casas decimais.
        return numero.quantize(Decimal("0.01"))

    except (InvalidOperation, TypeError, ValueError) as erro:
        raise ValueError(
            f"Não foi possível converter o valor monetário: {valor}"
        ) from erro

# A5

def remover_pedidos_duplicados(pedidos):
    """
    Regra A5: remove pedidos com IDs duplicados.

    Mantém a primeira ocorrência de cada ID, respeitando
    a ordem original dos registros extraídos.

    Retorna:
        - Lista de pedidos sem duplicatas.
        - Quantidade de registros descartados.
    """

    ids_encontrados = set()
    pedidos_unicos = []
    total_duplicados = 0

    for pedido in pedidos:
        pedido_id = pedido["id"]

        # Descarta o pedido caso seu ID já tenha sido encontrado.
        if pedido_id in ids_encontrados:
            total_duplicados += 1
            continue

        # Preserva apenas a primeira ocorrência de cada ID.
        ids_encontrados.add(pedido_id)
        pedidos_unicos.append(pedido)

    return pedidos_unicos, total_duplicados

## A6

def calcular_valores_pedido(pedido):
    """
    Regra A6: calcula o valor dos itens e identifica divergências.

    Compara o valor_total informado pela API com a soma
    das quantidades multiplicadas pelos preços unitários.

    Considera divergente uma diferença superior a R$ 0,01.

    Retorna:
        Cópia do pedido contendo:
        - valor_total convertido para Decimal
        - valor_itens calculado
        - divergente (True ou False)
    """

    # Preserva o pedido original.
    pedido_transformado = pedido.copy()

    valor_total = converter_valor_monetario(pedido["valor_total"])
    valor_itens = Decimal("0.00")

    # Calcula o subtotal de cada item e acumula o resultado.
    for item in pedido["itens"]:
        quantidade = int(item["quantidade"])
        preco_unitario = converter_valor_monetario(
            item["preco_unitario"]
        )

        valor_itens += quantidade * preco_unitario

    # Padroniza o resultado com duas casas decimais.
    valor_itens = valor_itens.quantize(Decimal("0.01"))

    # Verifica se a diferença ultrapassa a tolerância permitida.
    diferenca = abs(valor_total - valor_itens)
    divergente = diferenca > Decimal("0.01")

    pedido_transformado["valor_total"] = valor_total
    pedido_transformado["valor_itens"] = valor_itens
    pedido_transformado["divergente"] = divergente

    return pedido_transformado

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