
def tratar_emails_nulos(clientes):
    """
    Preserva todos os clientes e contabiliza os que possuem
    e-mail ausente ou nulo.

    Retorna:
        clientes: lista original de clientes
        total_nulos: quantidade de e-mails ausentes
    """

    # Inicia o contador de e-mails ausentes.
    total_nulos = 0

    # Percorre todos os clientes recebidos.
    for cliente in clientes:

        # .get() retorna None se a chave "email" não existir.
        # Também identificamos quando o valor é explicitamente None.
        if cliente.get("email") is None:
            total_nulos += 1

    # Nenhum cliente é removido ou alterado.
    return clientes, total_nulos

## funcao a2


def padronizar_estados(clientes):
    """
    Converte as siglas dos estados para letras maiúsculas.

    Retorna:
        clientes_transformados: lista com os estados padronizados
        total_alterados: quantidade de estados modificados
    """

    # Cria uma nova lista para armazenar os clientes transformados.
    clientes_transformados = []

    # Contador de estados que precisaram de alteração.
    total_alterados = 0

    # Percorre cada cliente recebido.
    for cliente in clientes:

        # Cria uma cópia para não modificar o registro original.
        cliente_transformado = cliente.copy()

        # Obtém a sigla do estado.
        estado_original = cliente_transformado["estado"]

        # Converte a sigla para maiúsculas.
        estado_padronizado = estado_original.upper()

        # Verifica se houve alguma alteração.
        if estado_original != estado_padronizado:
            total_alterados += 1

        # Atualiza o estado na cópia do cliente.
        cliente_transformado["estado"] = estado_padronizado

        # Adiciona o cliente transformado à nova lista.
        clientes_transformados.append(cliente_transformado)

    return clientes_transformados, total_alterados

## funcao a3

from datetime import datetime


def converter_data(valor):
    """
    Converte uma data em texto para um objeto date do Python.

    Formatos aceitos:
        YYYY-MM-DD
        DD/MM/YYYY

    Retorna:
        Um objeto date.

    Lança ValueError caso o formato seja inválido.
    """

    # Formatos de data aceitos pelo contrato.
    formatos = ["%Y-%m-%d", "%d/%m/%Y"]

    # Tenta interpretar a data em cada formato.
    for formato in formatos:
        try:
            # strptime interpreta o texto conforme o formato.
            # .date() mantém somente a data, sem horário.
            return datetime.strptime(valor, formato).date()

        except ValueError:
            # Se o formato não corresponder, tenta o próximo.
            continue

    # Nenhum dos formatos conseguiu interpretar a data.
    raise ValueError(f"Formato de data inválido: {valor}")

## funcao a4


from decimal import Decimal, InvalidOperation


def converter_valor_monetario(valor):
    """
    Converte números e textos com vírgula decimal
    para Decimal com duas casas decimais.

    Retorna:
        Decimal: valor monetário convertido.

    Lança:
        ValueError: quando o valor não é válido.
    """

    try:
        # Converte o valor recebido para texto.
        # Isso permite tratar tanto números quanto strings.
        texto = str(valor).strip()

        # Substitui a vírgula decimal por ponto.
        texto = texto.replace(",", ".")

        # Decimal evita problemas de precisão típicos do float.
        numero = Decimal(texto)

        # Rejeita valores especiais como NaN e Infinity.
        if not numero.is_finite():
            raise ValueError(f"Valor monetário inválido: {valor}")

        # Padroniza o valor com duas casas decimais.
        return numero.quantize(Decimal("0.01"))

    except (InvalidOperation, TypeError, ValueError) as erro:
        raise ValueError(
            f"Não foi possível converter o valor monetário: {valor}"
        ) from erro

# funcao a5


def remover_pedidos_duplicados(pedidos):
    """
    Remove pedidos com IDs repetidos, mantendo a primeira ocorrência.

    Retorna:
        pedidos_unicos: lista de pedidos sem IDs duplicados
        total_duplicados: quantidade de registros descartados
    """

    # Conjunto que armazena os IDs já encontrados.
    ids_encontrados = set()

    # Lista que receberá apenas a primeira ocorrência de cada pedido.
    pedidos_unicos = []

    # Contador de registros duplicados descartados.
    total_duplicados = 0

    # Percorre os pedidos na ordem em que foram extraídos.
    for pedido in pedidos:

        # Identifica o pedido pelo seu ID.
        pedido_id = pedido["id"]

        # Se o ID já foi encontrado, descarta esta ocorrência.
        if pedido_id in ids_encontrados:
            total_duplicados += 1
            continue

        # Registra o ID para identificar possíveis repetições.
        ids_encontrados.add(pedido_id)

        # Preserva a primeira ocorrência do pedido.
        pedidos_unicos.append(pedido)

    return pedidos_unicos, total_duplicados


## calculo valor de pedido A6


def calcular_valores_pedido(pedido):
    """
    Calcula o valor dos itens de um pedido e identifica divergências.

    Retorna:
        Uma cópia do pedido contendo:
        - valor_total convertido
        - valor_itens calculado
        - divergente (True ou False)
    """

    # Cria uma cópia para preservar o pedido original.
    pedido_transformado = pedido.copy()

    # Converte o valor total informado pela API.
    valor_total = converter_valor_monetario(pedido["valor_total"])

    # Inicia a soma dos itens em zero.
    valor_itens = Decimal("0.00")

    # Percorre os itens associados ao pedido.
    for item in pedido["itens"]:

        # Converte a quantidade para inteiro.
        quantidade = int(item["quantidade"])

        # Converte o preço unitário para Decimal.
        preco_unitario = converter_valor_monetario(
            item["preco_unitario"]
        )

        # Calcula o subtotal e adiciona ao total.
        valor_itens += quantidade * preco_unitario

    # Garante duas casas decimais.
    valor_itens = valor_itens.quantize(Decimal("0.01"))

    # Calcula a diferença absoluta entre os valores.
    diferenca = abs(valor_total - valor_itens)

    # Considera divergente apenas uma diferença superior a R$ 0,01.
    divergente = diferenca > Decimal("0.01")

    # Adiciona os resultados ao pedido transformado.
    pedido_transformado["valor_total"] = valor_total
    pedido_transformado["valor_itens"] = valor_itens
    pedido_transformado["divergente"] = divergente

    return pedido_transformado

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