# Entrega — Desafio ETL Verdejar

## 1. Repositório

**GitHub:** https://github.com/Zahard-b/desafio-final-bruno-araujo

**Branch de desenvolvimento:** `feat/etl-pipeline`

**Pull Request:** https://github.com/Zahard-b/desafio-final-bruno-araujo/pull/1

## 2. Resumo da implementação

O projeto implementa um pipeline ETL em Python e PostgreSQL, contemplando:

- Extração paginada de clientes e pedidos via API REST e leitura de produtos em CSV.
- Transformações de qualidade dos dados conforme as regras A1–A6.
- Carga transacional no PostgreSQL, com operações idempotentes.
- Consultas SQL de validação e reconciliação financeira.
- Testes automatizados com `pytest`.

## 3. Resultados verificados

| Indicador | Resultado |
|---|---:|
| Clientes carregados | 1.000 |
| Produtos carregados | 12 |
| Pedidos únicos carregados | 5.000 |
| Itens de pedidos carregados | 12.455 |
| Pedidos duplicados descartados | 100 |
| Pedidos com divergência financeira | 238 |
| Diferença na reconciliação | R$ 0,00 |
| Testes automatizados aprovados | 7 |

## 4. Vídeo de demonstração

**Link:** Pendente de gravação.

O vídeo deverá apresentar a estrutura do projeto, a execução do pipeline, os resultados no PostgreSQL e as verificações realizadas.

## 5. Reflexão sobre o desenvolvimento

O desenvolvimento foi organizado em etapas de extração, transformação, carga e validação, permitindo verificar os resultados de cada componente antes de avançar.

A principal preocupação foi garantir a consistência dos dados, especialmente no tratamento de pedidos duplicados, nos cálculos monetários e na reconciliação entre Python e PostgreSQL.

Os testes automatizados ajudaram a verificar as regras de transformação e a consistência dos dados carregados. A reexecução do pipeline também permitiu verificar que as quantidades de registros permaneceram estáveis.