import json
import os
from decimal import Decimal

import psycopg2
import pytest

from etl.transformacao import transformar_pedidos


def test_reconciliacao_pedidos():
    # Lê os pedidos brutos preservados na extração.
    with open("brutos/pedidos.json", encoding="utf-8") as arquivo:
        pedidos_brutos = json.load(arquivo)

    # Remove duplicatas e calcula os valores dos itens.
    pedidos, _ = transformar_pedidos(pedidos_brutos)

    quantidade_origem = len(pedidos)
    soma_origem = sum(
        (pedido["valor_itens"] for pedido in pedidos),
        Decimal("0.00")
    )

    # A senha é obtida de uma variável de ambiente.
    # Nunca deve ser escrita diretamente no código.
    senha = os.environ.get("PGPASSWORD")

    if not senha:
        pytest.fail("Defina PGPASSWORD antes de executar a reconciliação.")

    # Abre a conexão com o banco.
    conexao = psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        dbname="verdejar",
        user="postgres",
        password=senha,
        options="-c lc_messages=C"
    )

    try:
        # Consulta a quantidade e a soma armazenadas.
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(valor_itens), 0)
                FROM public.pedidos
            """)

            quantidade_banco, soma_banco = cursor.fetchone()

        # Verifica a quantidade de pedidos.
        assert quantidade_origem == quantidade_banco

        # A soma financeira deve ser exatamente igual.
        diferenca = abs(soma_origem - Decimal(soma_banco))


        assert diferenca == Decimal("0.00"), (
            f"Divergência financeira encontrada: R$ {diferenca}"
        )

    finally:
        # Fecha a conexão mesmo quando ocorre uma falha.
        conexao.close()