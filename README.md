# Verdejar — Pipeline ETL

Pipeline de engenharia de dados desenvolvido como parte do desafio final do **Bootcamp AIR Fellowship**, com foco em extração, transformação, carga e validação de dados utilizando Python e PostgreSQL.

O projeto integra informações de clientes, pedidos e produtos provenientes de uma API REST e de um arquivo CSV, aplicando regras de qualidade antes da persistência em um banco de dados relacional.

## Visão geral

O processamento é organizado em três etapas:

1. **Extração:** coleta paginada de clientes e pedidos via API REST e leitura do catálogo de produtos em CSV.
2. **Transformação:** padronização de dados, conversão de tipos, remoção de duplicatas e identificação de divergências financeiras.
3. **Carga:** persistência no PostgreSQL com controle transacional e operações que permitem reexecução sem duplicação de registros.

O projeto também inclui testes automatizados e reconciliação entre os dados transformados e os dados armazenados.

## Tecnologias

| Tecnologia | Finalidade |
|---|---|
| Python | Implementação do pipeline ETL |
| PostgreSQL | Armazenamento relacional |
| psycopg2 | Comunicação com o banco de dados |
| pytest | Testes automatizados |
| Git | Controle de versão |

## Estrutura do projeto

```text
.
├── etl/
│   ├── extracao.py
│   ├── transformacao.py
│   ├── carga.py
│   └── pipeline.py
├── tests/
│   ├── test_transformacao.py
│   └── test_reconciliacao.py
├── insumos/
│   ├── api_verdejar.py
│   ├── gerar_dados.py
│   ├── schema.sql
│   └── dados/
├── README.md
└── ...
```

O diretório `brutos/` é utilizado para preservar os dados extraídos durante o processamento e não é versionado no repositório.

## Execução

### Pré-requisitos

- Python 3.14 ou versão compatível com as dependências utilizadas.
- PostgreSQL instalado e em execução.
- Banco de dados `verdejar` configurado.
- Estrutura das tabelas criada a partir de `insumos/schema.sql`.
- Arquivos de dados brutos disponíveis para processamento.

### Instalação das dependências

Na raiz do projeto, execute:

```powershell
python -m pip install requests psycopg2-binary pytest
```

### Configuração do banco de dados

O ambiente utilizado no desenvolvimento possui as seguintes configurações:

| Parâmetro | Valor |
|---|---|
| Host | `127.0.0.1` |
| Porta | `5432` |
| Banco | `verdejar` |
| Usuário | `postgres` |

A senha deve ser fornecida por variável de ambiente, sem ser armazenada no código-fonte.

No PowerShell:

```powershell
$env:PGPASSWORD = Read-Host "Senha do PostgreSQL"


```
### Extração dos dados

Antes de executar a extração, é necessário iniciar a API Verdejar.

No primeiro terminal, a partir da raiz do projeto:

```powershell
cd insumos
python api_verdejar.py
```

Mantenha esse terminal aberto.

Em um segundo terminal, na raiz do projeto, execute:

```powershell
python -m etl.extracao
```

A extração consulta as rotas de clientes e pedidos em páginas de 50 registros e preserva os dados brutos na pasta `brutos/`, juntamente com o catálogo de produtos em CSV.

Essa etapa deve ser realizada antes da primeira execução do pipeline.

### Execução do pipeline

Após concluir a extração e configurar o PostgreSQL, execute na raiz do projeto:

```powershell
python -m etl.pipeline
```

O comando lê os arquivos preservados em `brutos/`, aplica as regras de transformação e carrega os dados nas quatro tabelas do PostgreSQL.

A carga utiliza transações e operações de atualização em caso de conflito, permitindo a reexecução sem duplicar registros.

## Regras de transformação

As transformações foram implementadas em funções independentes, seguindo as regras A1–A6 estabelecidas no desafio.

| Regra | Descrição | Resultado |
|---|---|---|
| A1 | Identificação e tratamento de e-mails nulos | 81 ocorrências |
| A2 | Padronização de siglas de estados | 151 alterações |
| A3 | Conversão de datas para formato consistente | 1.000 datas de clientes |
| A4 | Conversão de valores monetários para `Decimal` | Valores padronizados |
| A5 | Remoção de pedidos duplicados por identificador | 100 duplicatas removidas |
| A6 | Cálculo dos valores dos itens e identificação de divergências | 238 pedidos divergentes |

A regra A6 considera divergente um pedido cuja diferença absoluta entre o valor declarado e o valor calculado dos itens seja superior a R$ 0,01.

## Resultados do processamento

### Extração

| Fonte | Registros extraídos |
|---|---:|
| Clientes (API) | 1.000 |
| Pedidos (API) | 5.100 |
| Produtos (CSV) | 12 |

A extração utilizou páginas de 50 registros, totalizando 20 páginas de clientes e 102 páginas de pedidos.

### Carga

| Tabela | Registros carregados |
|---|---:|
| `clientes` | 1.000 |
| `produtos` | 12 |
| `pedidos` | 5.000 |
| `itens_pedido` | 12.455 |

A diferença entre os pedidos extraídos e carregados corresponde aos 100 registros duplicados removidos durante a transformação.

## Integridade e idempotência

A carga utiliza instruções SQL parametrizadas e operações `INSERT ... ON CONFLICT DO UPDATE`.

As operações são executadas dentro de uma transação, com confirmação por `COMMIT` e reversão por `ROLLBACK` em caso de falha.

A idempotência foi verificada mediante duas execuções consecutivas do pipeline. Após a segunda execução, as quatro tabelas mantiveram as mesmas quantidades de registros.

## Testes automatizados

A suíte de testes foi desenvolvida utilizando `pytest` e contempla:

- Seis testes para as regras de transformação A1–A6.
- Um teste de reconciliação entre os pedidos transformados em Python e os registros armazenados no PostgreSQL.

Para executar:

```powershell
python -m pytest tests/ -v
```

O teste de reconciliação requer que o PostgreSQL esteja acessível, com os dados carregados e a variável `PGPASSWORD` configurada.

**Resultado da execução conjunta: 7 testes aprovados.**

## Reconciliação financeira

A reconciliação verifica a consistência entre os valores calculados durante a transformação e os valores persistidos no banco.

| Indicador | Resultado |
|---|---:|
| Pedidos únicos na origem transformada | 5.000 |
| Pedidos no PostgreSQL | 5.000 |
| Soma de `valor_itens` em Python | R$ 311.228,75 |
| Soma de `valor_itens` no PostgreSQL | R$ 311.228,75 |
| Diferença financeira | R$ 0,00 |

O teste automatizado compara a quantidade de pedidos e a soma dos valores, exigindo igualdade entre os resultados calculados em Python e os armazenados no PostgreSQL, com diferença financeira de R$ 0,00.

## Consultas de validação

O arquivo `consultas_validacao.sql` contém quatro consultas utilizadas para verificar os dados armazenados no PostgreSQL.

| Consulta | Verificação | Resultado |
|---|---|---|
| V1 | Quantidade e valor dos pedidos agrupados por mês | Total geral de R$ 311.228,75 |
| V2 | Quantidade de pedidos agrupados por estado | 5.000 pedidos no total |
| V3 | Pedidos com divergência financeira | 238 pedidos |
| V4 | Reconciliação entre a soma mensal e o total geral | Diferença de R$ 0,00 |

As consultas foram executadas no PostgreSQL e apresentaram resultados consistentes com as transformações realizadas em Python.

## Documentação complementar

- `CONTRATO_DE_DADOS.md` — definição dos campos, tipos e regras de tratamento.
- `COMO_USEI_IA.md` — registro do uso de inteligência artificial, incluindo sugestões aceitas, rejeitadas e correções realizadas.
- `consultas_validacao.sql` — consultas SQL utilizadas para validação dos resultados.

## Autor

**Bruno Araújo**

Bootcamp AIR Fellowship — Desafio Final de Engenharia de Dados e Inteligência Artificial.
