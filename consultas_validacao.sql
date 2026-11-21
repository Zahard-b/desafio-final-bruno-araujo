-- =========================================================
-- DESAFIO VERDEJAR - CONSULTAS DE VALIDACAO
-- =========================================================

-- V1: Quantidade de pedidos e vendas por mes
SELECT
    DATE_TRUNC('month', data_pedido)::date AS mes,
    COUNT(*) AS quantidade_pedidos,
    SUM(valor_itens) AS total_vendas
FROM public.pedidos
GROUP BY DATE_TRUNC('month', data_pedido)
ORDER BY mes;


-- V2: Quantidade de pedidos por estado
SELECT
    c.estado,
    COUNT(*) AS quantidade_pedidos
FROM public.pedidos AS p
JOIN public.clientes AS c
    ON p.cliente_id = c.id
GROUP BY c.estado
ORDER BY quantidade_pedidos DESC;


-- V3: Pedidos com divergencia financeira superior a R$ 0,01
SELECT
    id,
    valor_total,
    valor_itens,
    ABS(valor_total - valor_itens) AS diferenca
FROM public.pedidos
WHERE ABS(valor_total - valor_itens) > 0.01
ORDER BY diferenca DESC;


-- V4: Reconciliacao entre soma mensal e total geral
WITH vendas_mensais AS (
    SELECT
        DATE_TRUNC('month', data_pedido) AS mes,
        SUM(valor_itens) AS total_mes
    FROM public.pedidos
    GROUP BY DATE_TRUNC('month', data_pedido)
)
SELECT
    (SELECT SUM(total_mes) FROM vendas_mensais) AS soma_mensal,
    (SELECT SUM(valor_itens) FROM public.pedidos) AS total_geral,
    (
        SELECT SUM(total_mes) FROM vendas_mensais
    ) - (
        SELECT SUM(valor_itens) FROM public.pedidos
    ) AS diferenca;