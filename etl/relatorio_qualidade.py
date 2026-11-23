from datetime import datetime
from pathlib import Path


def gerar_relatorio_qualidade(metricas, pasta_destino="relatorios"):
    """
    Gera um relatório de qualidade após uma execução do ETL.

    Parâmetros:
        metricas: dicionário com os contadores das regras A1–A6.
        pasta_destino: diretório onde o relatório será salvo.

    Retorna:
        Caminho do arquivo gerado.
    """

    # Registra a data e a hora da execução.
    agora = datetime.now()

    # Cria a pasta de relatórios, caso ainda não exista.
    pasta = Path(pasta_destino)
    pasta.mkdir(parents=True, exist_ok=True)

    # Utiliza a data e a hora para identificar cada relatório.
    nome_arquivo = agora.strftime("qualidade_%Y%m%d_%H%M%S_%f.txt")
    caminho = pasta / nome_arquivo

    # Organiza o conteúdo que será gravado.
    linhas = [
        "RELATÓRIO DE QUALIDADE — VERDEJAR",
        "",
        f"Data e hora: {agora:%d/%m/%Y %H:%M:%S}",
        "",
        f"A1 - E-mails nulos: {metricas['emails_nulos']}",
        f"A2 - Estados padronizados: {metricas['estados_padronizados']}",
        f"A3 - Datas convertidas: {metricas['datas_convertidas']}",
        f"A4 - Valores monetários convertidos: {metricas['valores_convertidos']}",
        f"A5 - Duplicados descartados: {metricas['duplicados_descartados']}",
        f"A6 - Pedidos divergentes: {metricas['pedidos_divergentes']}",
    ]

    # Grava as linhas no arquivo de texto.
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"Relatório de qualidade gerado: {caminho}")

    return caminho