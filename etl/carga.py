def carregar_produtos(conexao, produtos):
    """
    Insere ou atualiza produtos no PostgreSQL.

    Recebe:
        conexao: conexão aberta com o banco
        produtos: lista de produtos já transformados

    Retorna:
        Quantidade de produtos processados.
    """

    # Abre um cursor para executar comandos SQL.
    with conexao.cursor() as cursor:

        # Percorre os produtos transformados.
        for produto in produtos:

            # SQL parametrizado: os valores são enviados separadamente.
            cursor.execute(
                """
                INSERT INTO produtos (
                    produto_id, nome, categoria, preco_base
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (produto_id)
                DO UPDATE SET
                    nome = EXCLUDED.nome,
                    categoria = EXCLUDED.categoria,
                    preco_base = EXCLUDED.preco_base
                """,
                (
                    produto["produto_id"],
                    produto["nome"],
                    produto["categoria"],
                    produto["preco_base"]
                )
            )

    # Não executamos commit aqui.
    # O pipeline controlará a transação completa.
    return len(produtos)


def carregar_clientes(conexao, clientes):
    """
    Insere ou atualiza clientes no PostgreSQL.

    Recebe:
        conexao: conexão aberta com o banco
        clientes: lista de clientes já transformados

    Retorna:
        Quantidade de clientes processados.
    """

    # Abre um cursor para executar comandos SQL.
    with conexao.cursor() as cursor:

        # Percorre os clientes transformados.
        for cliente in clientes:

            # Insere um cliente ou atualiza seus dados caso o ID já exista.
            cursor.execute(
                """
                INSERT INTO clientes (
                    id, nome, email, cidade, estado, cadastro_em
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    nome = EXCLUDED.nome,
                    email = EXCLUDED.email,
                    cidade = EXCLUDED.cidade,
                    estado = EXCLUDED.estado,
                    cadastro_em = EXCLUDED.cadastro_em
                """,
                (
                    cliente["id"],
                    cliente["nome"],
                    cliente.get("email"),
                    cliente["cidade"],
                    cliente["estado"],
                    cliente["cadastro_em"]
                )
            )

    # O pipeline será responsável por confirmar a transação.
    return len(clientes)

def carregar_pedidos(conexao, pedidos):
    """
    Insere ou atualiza pedidos no PostgreSQL.

    Recebe:
        conexao: conexão aberta com o banco
        pedidos: lista de pedidos únicos e transformados

    Retorna:
        Quantidade de pedidos processados.
    """

    # Abre um cursor para executar os comandos SQL.
    with conexao.cursor() as cursor:

        # Percorre os pedidos já transformados.
        for pedido in pedidos:

            # Insere ou atualiza o pedido pela chave primária id.
            cursor.execute(
                """
                INSERT INTO pedidos (
                    id, cliente_id, data_pedido, status,
                    valor_total, valor_itens, divergente
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    cliente_id = EXCLUDED.cliente_id,
                    data_pedido = EXCLUDED.data_pedido,
                    status = EXCLUDED.status,
                    valor_total = EXCLUDED.valor_total,
                    valor_itens = EXCLUDED.valor_itens,
                    divergente = EXCLUDED.divergente
                """,
                (
                    pedido["id"],
                    pedido["cliente_id"],
                    pedido["data_pedido"],
                    pedido["status"],
                    pedido["valor_total"],
                    pedido["valor_itens"],
                    pedido["divergente"]
                )
            )

    # O pipeline será responsável pelo commit ou rollback.
    return len(pedidos)

def carregar_itens_pedido(conexao, itens):
    """
    Insere ou atualiza os itens dos pedidos no PostgreSQL.

    A chave primária é composta por (pedido_id, linha).
    Retorna a quantidade de itens processados.
    """

    # Abre um cursor para executar os comandos SQL.
    with conexao.cursor() as cursor:

        # Percorre os itens já transformados.
        for item in itens:

            # Insere o item ou atualiza os dados caso a chave já exista.
            cursor.execute(
                """
                INSERT INTO itens_pedido (
                    pedido_id, linha, produto_id,
                    quantidade, preco_unitario
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (pedido_id, linha)
                DO UPDATE SET
                    produto_id = EXCLUDED.produto_id,
                    quantidade = EXCLUDED.quantidade,
                    preco_unitario = EXCLUDED.preco_unitario
                """,
                (
                    item["pedido_id"],
                    item["linha"],
                    item["produto_id"],
                    item["quantidade"],
                    item["preco_unitario"]
                )
            )

    # O pipeline controlará o commit ou rollback.
    return len(itens)