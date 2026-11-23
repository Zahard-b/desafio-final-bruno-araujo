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

**Link:** [Assistir à defesa oral no YouTube](https://youtu.be/SvbxeVqJm5U)

O vídeo deverá apresentar a estrutura do projeto, a execução do pipeline, os resultados no PostgreSQL e as verificações realizadas.

## 5. Como usei IA

### Registro de Uso de Inteligência Artificial

#### 1. Contexto

Durante o desenvolvimento do ETL Verdejar, utilizei o ChatGPT como **par de programação com escopo limitado**, conforme as orientações do desafio.

A ferramenta auxiliou na compreensão de requisitos, na elaboração de funções específicas, na criação de testes e na investigação de erros.

Fiquei responsável por executar os comandos, verificar os resultados, corrigir problemas e decidir quais sugestões aceitar ou rejeitar.

As tarefas solicitadas à IA foram delimitadas por funcionalidade, como a conversão de valores monetários, a remoção de pedidos duplicados e a elaboração de testes para regras específicas. Cada função foi executada e verificada antes da continuidade do desenvolvimento. A integração das etapas foi realizada progressivamente, com validações no terminal e no PostgreSQL.

#### 2. Sugestões aceitas

| Sugestão | Justificativa e validação |
|---|---|
| Utilizar `Decimal` para valores monetários | Pedi ajuda para converter valores recebidos como número ou texto com vírgula. Aceitei `Decimal` para preservar a precisão dos cálculos em centavos. Validei a conversão com o teste A4 e conferi que a soma de `valor_itens` no Python e no PostgreSQL foi de R$ 311.228,75, com diferença de R$ 0,00. |
| Criar testes automatizados com `pytest` | Permitiu validar individualmente as seis regras de transformação e a reconciliação. Nessa primeira rodada, antes do teste do relatório de qualidade, os sete testes passaram. |
| Utilizar `ON CONFLICT DO UPDATE` na carga | Pedi ajuda para reexecutar a carga sem duplicar registros. Aceitei a sugestão porque, quando a chave já existe, o PostgreSQL atualiza a linha existente. Validei a decisão rodando o pipeline duas vezes e conferindo no PostgreSQL que as contagens foram mantidas: 12 produtos, 1.000 clientes, 5.000 pedidos e 12.455 itens. |

#### 3. Sugestões rejeitadas ou adaptadas

| Sugestão | Motivo da decisão |
|---|---|
| Deixar a separação de `transformacao.py` para depois da entrega | Adaptei o momento da sugestão e fiz a separação antes de gravar. Coloquei as regras A1–A6 em `etl/regras_transformacao.py` e mantive o processamento em lote e os contadores em `etl/transformacao.py`. Validei a mudança com oito testes aprovados, uma execução da carga e a conferência dos seis indicadores no relatório. |
| Criar um arquivo separado apenas para testar a regra A6 | Pedi ajuda para conferir o cálculo dos itens e a marcação de divergência. Rejeitei o arquivo separado porque a verificação pontual podia ser feita no terminal. A validação permanente ficou em `tests/test_transformacao.py`: o teste A6 passou e confirmou que R$ 0,01 de diferença fica dentro da tolerância e que R$ 0,02 é marcado como divergência. |
| Repetir a execução de `etl.pipeline` após uma falha de importação | Pedi ajuda porque `python -m etl.pipeline` retornava `No module named etl.pipeline`. Antes de repetir o comando, conferi a estrutura do projeto e encontrei `pipeline.py` em `etl/__pycache__`. Corrigi a localização e a indentação do arquivo. Depois rodei o mesmo comando e confirmei que o pipeline executava e carregava as quatro tabelas. |

#### 4. Falhas e retrabalho

##### Extração da API

A implementação inicial precisou ser revisada para tratar erros de conexão e respostas HTTP inválidas.

Após a correção, testei uma conexão recusada e uma rota inexistente, que retornou HTTP 404.

##### Consulta SQL no pgAdmin

Na Sprint 1, usei a IA como tutora para entender as consultas SQL e investigar erros no pgAdmin. Eu executei as consultas e conferi os resultados. Na validação de vendas, comparei a soma dos meses com o total geral: ambos deram R$ 311.228,75, com diferença de R$ 0,00.

Uma orientação incompleta fez com que um `ORDER BY` antigo permanecesse no editor, provocando o erro:

```text
SQL state: 42601
```

O problema foi resolvido removendo a consulta anterior antes de executar o novo SQL.

##### Teste de reconciliação

O teste falhou inicialmente porque a variável `PGPASSWORD` não estava configurada.

Após configurar a variável de ambiente e executar novamente, o teste passou.

##### Organização do código de transformação

Durante a revisão das funções A1–A6, os testes identificaram
um erro `NameError: name 'A1' is not defined`.

O problema ocorreu porque a identificação de uma seção
estava escrita sem o caractere `#`, sendo interpretada
como código Python.

Após corrigir o comentário, executei novamente os testes
e confirmei que as seis regras continuavam funcionando.

#### 5. Evidências de validação

| Verificação | Resultado |
|---|---|
| Suíte completa após o Stretch 3 | 8 testes aprovados |
| Pedidos duplicados removidos | 100 |
| Pedidos divergentes | 238 |
| Pedidos carregados | 5.000 |
| Reconciliação financeira | Diferença de R$ 0,00 |
| Idempotência | Quantidades mantidas após reexecução |

Exemplos de interações e resultados registrados durante o desenvolvimento:

**Decisão de rejeitar um arquivo adicional:**

> Eu não vou criar um arquivo novo somente para o A6, faça rodar tudo.

**Erro encontrado no pgAdmin:**

```text
ERROR: erro de sintaxe em ou próximo a "ORDER"
SQL state: 42601
```

**Resultados do pytest:**

- Antes do teste do relatório de qualidade: `7 passed`.
- Suíte completa com o teste do relatório de qualidade: `8 passed`.

#### 6. Conclusão

A IA contribuiu para esclarecer dúvidas, sugerir soluções pontuais e auxiliar na investigação de erros.

Entretanto, nem todas as sugestões foram utilizadas. Algumas precisaram ser adaptadas e outras foram rejeitadas após avaliar sua necessidade.

A execução dos testes, a correção dos problemas e a validação dos resultados foram fundamentais para compreender o funcionamento do ETL e garantir a consistência dos dados.

#### Uso de IA — Stretch 3: Relatório de Qualidade

**Objetivo:** implementar um relatório automático com a data e hora da execução e os contadores das seis regras de transformação (A1–A6).

**Sugestão da IA:** criar um módulo separado (`etl/relatorio_qualidade.py`) para gerar arquivos `.txt`, utilizando `datetime` para registrar a execução e `pathlib` para organizar os arquivos. Também sugeriu integrar a geração ao `pipeline.py` após a carga no PostgreSQL.

**Decisão tomada:** aceitei a separação do relatório em um módulo próprio para manter o pipeline mais organizado. Optei por gerar um arquivo por execução e ignorar a pasta `relatorios/` no Git, evitando versionar arquivos gerados automaticamente.

**Validação realizada:** primeiro verifiquei a sintaxe do módulo com `py_compile`. Depois, gerei um relatório com dados fictícios e conferi seu conteúdo. Em seguida, executei o ETL com os dados reais e confirmei os seis indicadores: A1 = 81, A2 = 151, A3 = 6.000, A4 = 17.467, A5 = 100 e A6 = 238. Por fim, criei um teste automatizado para o relatório e executei toda a suíte, obtendo **8 testes aprovados**.

**Limitação identificada:** o indicador A4 contabiliza os campos monetários preparados para carga, e não necessariamente cada chamada realizada à função de conversão.

## 6. Reflexão sobre o desenvolvimento

1. Qual foi a decisão mais difícil do ETL e por quê?

Minha maior dificuldade foi organizar o projeto e entender como cada etapa se conectava. Como ainda estou aprendendo, tive dúvidas sobre a estrutura dos arquivos, a configuração do ambiente e a ordem das atividades. Decidi desenvolver tudo aos poucos, testando cada etapa antes de avançar, o que me ajudou a entender melhor o funcionamento do ETL.

2. O que você delegou à IA e o que fez questão de fazer sozinho?

Utilizei a IA principalmente para tirar dúvidas, entender os requisitos e receber orientações sobre como organizar o projeto. Também pedi ajuda com funções específicas e testes. Fiz questão de executar os comandos, conferir os resultados e questionar sugestões que não faziam sentido ou apresentavam erros.

3. Se tivesse mais uma semana, o que mudaria primeiro?

Eu gostaria de ter desenvolvido o projeto com mais calma, dedicando mais tempo para entender e absorver o funcionamento de cada etapa. Também revisaria o código para identificar partes que poderiam ser simplificadas ou processos desnecessários que poderiam ser removidos, deixando o ETL mais organizado, fácil de entender e manter.