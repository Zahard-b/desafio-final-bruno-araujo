# Contrato de Dados — ETL Verdejar

## 1. Objetivo

Documentar a estrutura das tabelas de destino no PostgreSQL, os tipos de dados esperados, as regras de transformação e as condições de nulidade.

As definições foram verificadas diretamente no banco de dados `verdejar`, criado a partir do esquema fornecido no desafio.

## 2. Tabela `clientes`

| Campo | Tipo | Aceita NULL | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Preservar o identificador inteiro recebido da API |
| nome | TEXT | Não | Preservar o valor |
| email | TEXT | Sim | Preservar valores nulos |
| cidade | TEXT | Não | Preservar o valor |
| estado | CHAR(2) | Não | Converter para maiúsculas |
| cadastro_em | DATE | Não | Converter para data |

### Regras de qualidade

**A1 — E-mails nulos**

Clientes com e-mail ausente ou nulo devem ser preservados na carga. O processo deve contabilizar quantos registros apresentam essa condição.

**A2 — Padronização de estados**

As siglas de estado devem ser convertidas para letras maiúsculas. O processo deve contabilizar quantos registros precisaram de alteração.

**A3 — Conversão de datas**

Datas recebidas nos formatos `YYYY-MM-DD` e `DD/MM/YYYY` devem ser convertidas para valores de data compatíveis com PostgreSQL.

### Validações previstas

- Verificar se a quantidade de clientes carregados corresponde à quantidade de clientes extraídos.
- Verificar se clientes sem e-mail foram preservados.
- Verificar se as siglas dos estados foram padronizadas.
- Verificar se as datas foram convertidas corretamente.

## 3. Tabela `produtos`

A tabela armazena os produtos disponíveis no catálogo da Verdejar.

Os dados são extraídos do arquivo `insumos/dados/produtos.csv`.

| Campo | Tipo PostgreSQL | Aceita NULL | Regra de transformação |
|---|---|---|---|
| produto_id | INTEGER | Não | Converter o identificador recebido como texto para inteiro |
| nome | TEXT | Não | Preservar o nome do produto |
| categoria | TEXT | Não | Preservar a categoria |
| preco_base | NUMERIC(10,2) | Não | Converter o preço recebido como texto para valor numérico |

### Regras de qualidade

**Conversão de tipos**

Como os dados são lidos utilizando `csv.DictReader`, os valores são inicialmente recebidos como texto. Os campos `produto_id` e `preco_base` devem ser convertidos para os tipos adequados antes da inserção no PostgreSQL.

Os preços são convertidos para Decimal, com duas casas decimais, evitando imprecisões associadas a números de ponto flutuante.

### Validações previstas

- Verificar se todos os produtos do CSV foram carregados.
- Verificar se os identificadores foram convertidos corretamente.
- Verificar se os preços foram convertidos para valores numéricos.
- Confirmar que os campos obrigatórios não possuem valores nulos.

**Quantidade de produtos identificados na origem:** 12.

## 4. Tabela `pedidos`

A tabela armazena os pedidos realizados pelos clientes da Verdejar.

Os dados são extraídos da rota `/pedidos` da API REST.

| Campo | Tipo PostgreSQL | Aceita NULL | Regra de transformação |
|---|---|---|---|
| id | INTEGER | Não | Preservar o identificador inteiro recebido da API e eliminar duplicatas, mantendo a primeira ocorrência |
| cliente_id | INTEGER | Não | Preservar o identificador inteiro do cliente recebido da API |
| data_pedido | DATE | Não | Converter para data válida |
| status | TEXT | Não | Preservar o status |
| valor_total | NUMERIC(12,2) | Não | Converter para valor decimal com duas casas |
| valor_itens | NUMERIC(12,2) | Não | Calcular a soma dos itens do pedido |
| divergente | BOOLEAN | Não | Indicar se existe divergência entre o valor total e a soma dos itens |

### Regras de qualidade

**A3 — Conversão de datas**

As datas recebidas nos formatos `YYYY-MM-DD` e `DD/MM/YYYY` devem ser convertidas para valores de data compatíveis com PostgreSQL.

**A4 — Conversão de valores monetários**

O campo `valor_total` pode conter números ou textos com vírgula decimal, como `"125,84"`.

Os valores devem ser convertidos para uma representação decimal com duas casas, evitando problemas de precisão.

**A5 — Eliminação de pedidos duplicados**

A extração pode retornar pedidos com o mesmo identificador em páginas diferentes.

O processo deve preservar a primeira ocorrência de cada ID, descartar as repetições e contabilizar quantos registros foram descartados.

**A6 — Reconciliação dos valores dos pedidos**

O campo `valor_itens` deve ser calculado a partir dos itens associados ao pedido:

`valor_itens = soma(quantidade × preco_unitario)`

O campo `valor_total` original deve ser preservado após sua conversão para decimal.

O campo `divergente` será definido como:

- `TRUE`: diferença absoluta entre `valor_total` e `valor_itens` superior a R$ 0,01.
- `FALSE`: diferença absoluta menor ou igual a R$ 0,01.

O processo deve contabilizar a quantidade de pedidos divergentes.

### Validações previstas

- Confirmar que os pedidos possuem IDs únicos após a transformação.
- Verificar se as datas foram convertidas corretamente.
- Verificar se os valores monetários possuem duas casas decimais.
- Confirmar que `valor_itens` corresponde à soma dos itens.
- Verificar se o campo `divergente` foi calculado corretamente.
- Contabilizar os pedidos duplicados descartados.
- Comparar a quantidade de pedidos únicos na origem com a quantidade carregada no PostgreSQL.

**Quantidade de registros brutos identificados na origem:** 5.100.

Após a aplicação da regra A5 sobre os 5.100 pedidos brutos, foram identificados 5.000 pedidos únicos e descartadas 100 duplicatas.

## 5. Tabela `itens_pedido`

A tabela armazena os produtos associados a cada pedido, incluindo quantidade e preço unitário.

Os registros são obtidos a partir dos itens presentes nos pedidos extraídos da API.

| Campo | Tipo PostgreSQL | Aceita NULL | Regra de transformação |
|---|---|---|---|
| pedido_id | INTEGER | Não | Associar o item ao identificador do pedido |
| linha | INTEGER | Não | Identificar a posição do item dentro do pedido |
| produto_id | INTEGER | Não | Converter o identificador do produto para inteiro |
| quantidade | INTEGER | Não | Converter a quantidade para inteiro |
| preco_unitario | NUMERIC(10,2) | Não | Converter o preço unitário para valor decimal |

### Regras de qualidade

**Conversão de tipos**

Os identificadores e as quantidades devem ser representados por números inteiros.

Os preços unitários devem ser convertidos para valores decimais adequados a cálculos monetários.

**Relacionamento com pedidos**

Cada item deve estar associado a um pedido existente na tabela `pedidos`.

Os itens de pedidos duplicados descartados durante a transformação não devem ser carregados novamente.

**Relacionamento com produtos**

O campo `produto_id` deve corresponder a um produto existente na tabela `produtos`.

**A6 — Cálculo do valor dos itens**

Para cada pedido, o processo deve calcular:

`valor_itens = soma(quantidade × preco_unitario)`

O resultado será utilizado para preencher o campo `valor_itens` da tabela `pedidos` e identificar possíveis divergências em relação ao `valor_total` informado pela API.

### Validações previstas

- Verificar se todos os itens pertencem a pedidos existentes.
- Verificar se os produtos referenciados existem.
- Confirmar que quantidades e preços foram convertidos corretamente.
- Confirmar que os itens dos pedidos duplicados não foram carregados duas vezes.
- Comparar a soma dos valores dos itens na origem transformada com a soma correspondente no PostgreSQL.

## 6. Resultados da validação

Após a execução do pipeline, foram confirmadas as seguintes quantidades no PostgreSQL:

| Tabela | Registros |
|---|---:|
| clientes | 1.000 |
| produtos | 12 |
| pedidos | 5.000 |
| itens_pedido | 12.455 |

A reconciliação entre os pedidos transformados em Python e os dados armazenados no PostgreSQL apresentou diferença financeira de R$ 0,00.

Os testes automatizados foram executados com sucesso, totalizando 8 testes aprovados.