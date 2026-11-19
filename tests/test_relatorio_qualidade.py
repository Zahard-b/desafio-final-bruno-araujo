from datetime import datetime

from etl.relatorio_qualidade import gerar_relatorio_qualidade


def test_gerar_relatorio_qualidade(tmp_path):
    metricas = {
        "emails_nulos": 2,
        "estados_padronizados": 3,
        "datas_convertidas": 10,
        "valores_convertidos": 15,
        "duplicados_descartados": 1,
        "pedidos_divergentes": 2,
    }

    caminho = gerar_relatorio_qualidade(
        metricas,
        pasta_destino=tmp_path
    )

    assert caminho.exists()

    conteudo = caminho.read_text(encoding="utf-8")

    assert "A1 - E-mails nulos: 2" in conteudo
    assert "A2 - Estados padronizados: 3" in conteudo
    assert "A3 - Datas convertidas: 10" in conteudo
    assert "A4 - Valores monetários convertidos: 15" in conteudo
    assert "A5 - Duplicados descartados: 1" in conteudo
    assert "A6 - Pedidos divergentes: 2" in conteudo

    assert "Data e hora:" in conteudo

    # Confere se o horário registrado tem o formato esperado.
    linha_data = next(
        linha for linha in conteudo.splitlines()
        if linha.startswith("Data e hora:")
    )
    data_texto = linha_data.split("Data e hora:", 1)[1].strip()
    datetime.strptime(data_texto, "%d/%m/%Y %H:%M:%S")