from datetime import date
from decimal import Decimal

import pytest

from etl.regras_transformacao import (
    tratar_emails_nulos,
    padronizar_estados,
    converter_data,
    converter_valor_monetario,
    remover_pedidos_duplicados,
    calcular_valores_pedido,
)

def test_a3_conversao_datas():
    # Verifica a conversão do formato ISO.
    assert converter_data("2025-04-04") == date(2025, 4, 4)

    # Verifica a conversão do formato brasileiro.
    assert converter_data("04/04/2025") == date(2025, 4, 4)

    # Uma data inválida deve gerar ValueError.
    with pytest.raises(ValueError):
        converter_data("31/02/2025")


def test_a4_conversao_valores_monetarios():
    # Valor numérico inteiro.
    assert converter_valor_monetario(10) == Decimal("10.00")

    # Valor com ponto decimal.
    assert converter_valor_monetario("15.50") == Decimal("15.50")

    # Valor com vírgula decimal.
    assert converter_valor_monetario("15,50") == Decimal("15.50")

    # Verifica o arredondamento para duas casas decimais.
    assert converter_valor_monetario("10.456") == Decimal("10.46")

    # Valor inválido deve gerar um erro.
    with pytest.raises(ValueError):
        converter_valor_monetario("abc")

def test_a5_remocao_duplicados():
    # Simula pedidos recebidos em diferentes páginas da API.
    pedidos = [
        {"id": 1, "valor_total": 100},
        {"id": 2, "valor_total": 200},
        {"id": 1, "valor_total": 999},
        {"id": 3, "valor_total": 300},
    ]

    # Executa a regra A5.
    pedidos_unicos, duplicados = remover_pedidos_duplicados(pedidos)

    # Deve manter apenas três pedidos.
    assert len(pedidos_unicos) == 3

    # Deve contabilizar uma duplicata descartada.
    assert duplicados == 1

    # Confirma que a primeira ocorrência do pedido 1 foi preservada.
    assert pedidos_unicos[0]["valor_total"] == 100

    # Confirma que a ordem original foi mantida.
    assert [pedido["id"] for pedido in pedidos_unicos] == [1, 2, 3]

def test_a1_emails_nulos():
    # Simula clientes com e sem e-mail.
    clientes = [
        {"id": 1, "email": "cliente@exemplo.com"},
        {"id": 2, "email": None},
        {"id": 3},
        {"id": 4, "email": "outro@exemplo.com"},
    ]

    # Executa a regra A1.
    clientes_tratados, quantidade_nulos = tratar_emails_nulos(clientes)

    # Deve identificar dois clientes sem e-mail.
    assert quantidade_nulos == 2

    # Nenhum cliente deve ser descartado.
    assert len(clientes_tratados) == 4

    # Os e-mails existentes devem permanecer inalterados.
    assert clientes_tratados[0]["email"] == "cliente@exemplo.com"

    # O e-mail nulo deve continuar nulo.
    assert clientes_tratados[1]["email"] is None

def test_a2_padronizacao_estados():
    # Simula clientes com estados em diferentes formatos.
    clientes = [
        {"id": 1, "estado": "sp"},
        {"id": 2, "estado": "RJ"},
        {"id": 3, "estado": "mg"},
        {"id": 4, "estado": "SC"},
    ]

    # Executa a transformação A2.
    clientes_tratados, quantidade_alterados = padronizar_estados(clientes)

    # Os quatro clientes devem ser preservados.
    assert len(clientes_tratados) == 4

    # Apenas dois estados precisavam ser padronizados.
    assert quantidade_alterados == 2

    # Todos os estados devem estar em maiúsculas.
    assert [cliente["estado"] for cliente in clientes_tratados] == [
        "SP", "RJ", "MG", "SC"
    ]

    # Os dados originais não devem ser modificados.
    assert clientes[0]["estado"] == "sp"

def test_a6_calculo_valores_pedido():
    # Pedido com dois itens: 2 x 10,00 + 1 x 5,00 = 25,00.
    pedido = {
        "id": 1,
        "valor_total": "25,00",
        "itens": [
            {"produto_id": 1, "quantidade": 2, "preco_unitario": "10,00"},
            {"produto_id": 2, "quantidade": 1, "preco_unitario": "5,00"},
        ],
    }

    # Calcula os valores e verifica um pedido sem divergência.
    resultado = calcular_valores_pedido(pedido)

    assert resultado["valor_itens"] == Decimal("25.00")
    assert resultado["valor_total"] == Decimal("25.00")
    assert resultado["divergente"] is False

    # Uma diferença de R$ 0,02 deve gerar divergência.
    pedido_divergente = pedido.copy()
    pedido_divergente["valor_total"] = "25,02"

    resultado_divergente = calcular_valores_pedido(pedido_divergente)

    assert resultado_divergente["divergente"] is True

    # Uma diferença de exatamente R$ 0,01 não deve gerar divergência.
    pedido_limite = pedido.copy()
    pedido_limite["valor_total"] = "25,01"

    resultado_limite = calcular_valores_pedido(pedido_limite)

    assert resultado_limite["divergente"] is False

    # A função não deve alterar o pedido original.
    assert pedido["valor_total"] == "25,00"