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
| Testes automatizados aprovados | 8 |

## 4. Vídeo de demonstração

**Link:** Pendente de gravação.

O vídeo deverá apresentar a estrutura do projeto, a execução do pipeline, os resultados no PostgreSQL e as verificações realizadas.

## 5. Reflexão sobre o desenvolvimento

1. Qual foi a decisão mais difícil do ETL e por quê?

Minha maior dificuldade foi organizar o projeto e entender como cada etapa se conectava. Como ainda estou aprendendo, tive dúvidas sobre a estrutura dos arquivos, a configuração do ambiente e a ordem das atividades. Decidi desenvolver tudo aos poucos, testando cada etapa antes de avançar, o que me ajudou a entender melhor o funcionamento do ETL.

2. O que você delegou à IA e o que fez questão de fazer sozinho?

Utilizei a IA principalmente para tirar dúvidas, entender os requisitos e receber orientações sobre como organizar o projeto. Também pedi ajuda com funções específicas e testes. Fiz questão de executar os comandos, conferir os resultados e questionar sugestões que não faziam sentido ou apresentavam erros.

3. Se tivesse mais uma semana, o que mudaria primeiro?

Eu gostaria de ter desenvolvido o projeto com mais calma, dedicando mais tempo para entender e absorver o funcionamento de cada etapa. Também revisaria o código para identificar partes que poderiam ser simplificadas ou processos desnecessários que poderiam ser removidos, deixando o ETL mais organizado, fácil de entender e manter.