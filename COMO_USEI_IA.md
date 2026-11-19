# Registro de Uso de Inteligência Artificial

## 1. Contexto

Durante o desenvolvimento do ETL Verdejar, utilizei o ChatGPT como **par de programação com escopo limitado**, conforme as orientações do desafio.

A ferramenta auxiliou na compreensão de requisitos, na elaboração de funções específicas, na criação de testes e na investigação de erros.

Fiquei responsável por executar os comandos, verificar os resultados, corrigir problemas e decidir quais sugestões aceitar ou rejeitar.

As tarefas solicitadas à IA foram delimitadas por funcionalidade, como a conversão de valores monetários, a remoção de pedidos duplicados e a elaboração de testes para regras específicas. Cada função foi executada e verificada antes da continuidade do desenvolvimento. A integração das etapas foi realizada progressivamente, com validações no terminal e no PostgreSQL.

## 2. Sugestões aceitas

| Sugestão | Justificativa e validação |
|---|---|
| Utilizar `Decimal` para valores monetários | Evitou problemas de precisão associados ao `float`. A reconciliação financeira apresentou diferença de R$ 0,00. |
| Criar testes automatizados com `pytest` | Permitiu validar individualmente as seis regras de transformação e a reconciliação. Os sete testes passaram. |
| Utilizar `ON CONFLICT DO UPDATE` na carga | Permitiu reexecutar o pipeline sem duplicar registros. As quantidades das quatro tabelas permaneceram iguais após a segunda execução. |

## 3. Sugestões rejeitadas ou adaptadas

| Sugestão | Motivo da decisão |
|---|---|
| Criar um arquivo separado apenas para testar a regra A6 | Preferi realizar a verificação diretamente pelo terminal, evitando arquivos temporários desnecessários. |
| Utilizar comandos extensos com `python -c` no PowerShell | Os comandos apresentaram problemas com aspas e sintaxe. Preferi instruções mais simples e fáceis de executar. |
| Repetir a execução de `etl.pipeline` após uma falha de importação | Adaptada: o comando retornava `No module named etl.pipeline`. Antes de repetir o comando, investiguei a estrutura do projeto e identifiquei que o arquivo havia sido criado incorretamente em `etl/__pycache__`. Corrigi sua localização e a indentação antes de executar novamente. |

## 4. Falhas e retrabalho

### Extração da API

A implementação inicial precisou ser revisada para tratar erros de conexão e respostas HTTP inválidas.

Após a correção, testei uma conexão recusada e uma rota inexistente, que retornou HTTP 404.

### Consulta SQL no pgAdmin

Uma orientação incompleta fez com que um `ORDER BY` antigo permanecesse no editor, provocando o erro:

```text
SQL state: 42601
```

O problema foi resolvido removendo a consulta anterior antes de executar o novo SQL.

### Teste de reconciliação

O teste falhou inicialmente porque a variável `PGPASSWORD` não estava configurada.

Após configurar a variável de ambiente e executar novamente, o teste passou.

### Organização do código de transformação

Durante a revisão das funções A1–A6, os testes identificaram
um erro `NameError: name 'A1' is not defined`.

O problema ocorreu porque a identificação de uma seção
estava escrita sem o caractere `#`, sendo interpretada
como código Python.

Após corrigir o comentário, executei novamente os testes
e confirmei que as seis regras continuavam funcionando.

## 5. Evidências de validação

| Verificação | Resultado |
|---|---|
| Testes automatizados | 7 aprovados |
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

**Resultado dos testes:**

```text
7 passed
```

## 6. Conclusão

A IA contribuiu para esclarecer dúvidas, sugerir soluções pontuais e auxiliar na investigação de erros.

Entretanto, nem todas as sugestões foram utilizadas. Algumas precisaram ser adaptadas e outras foram rejeitadas após avaliar sua necessidade.

A execução dos testes, a correção dos problemas e a validação dos resultados foram fundamentais para compreender o funcionamento do ETL e garantir a consistência dos dados.