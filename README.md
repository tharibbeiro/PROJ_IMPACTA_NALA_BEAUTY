# Nala Beauty BI

Projeto de faculdade de dados/BI: e-commerce fictício de maquiagem e produtos
de beleza, com 3 camadas — banco de dados, back-end e front-end.

## Arquitetura

```
SQL Server (dbo.*)  →  Python (backend/processar_metricas.py)  →  SQL Server (analytics.*)  →  Power BI
   dado bruto              aplica regras de negócio                 dado tratado              dashboard
```

## Estrutura

```
sql/
├── 01_criar_tabelas.sql      -- cria o banco Ecommerce_Nala_Beauty e as tabelas
└── 02_inserir_dados.sql      -- popula com dados fictícios
backend/
├── processar_metricas.py     -- calcula as métricas e grava em analytics.*
├── requirements.txt
└── .env.example             
data/
└── gerar_dados.py            -- gera o script 02_inserir_dados.sql
dashboard/
├── Nala Beauty BI.pbix       -- dashboard Power BI
└── logo_nala_beauty.png


## Como rodar

1. **Banco de dados**:
   Foi executado a criação do script `sql/01_criar_tabelas.sql` e depois `sql/02_inserir_dados.sql` no SQL Server.
2. **Back-end**:
   Refinamento e tratamentos dos dados do ecommerce para visualizar as metrícas de vendas utilizando python.  
   processar_metricas.py
   ```
## Métricas calculadas (schema `analytics`)
- `FaturamentoMensal` — faturamento por mês
- `FaturamentoPorCategoria` — faturamento por categoria de produto
- `TopProdutos` — top 10 produtos por faturamento
- `TicketMedioPorCliente` — ticket médio e qtd. de pedidos por cliente
- `PedidosPorStatus` — quantidade de pedidos por status
- `ClientesRecorrentes` — top 10 clientes com 2+ pedidos

3. **Dashboard**:
   Painel criado para acompanhamento e monitoramento das vendas:
   <img width="1317" height="737" alt="image" src="https://github.com/user-attachments/assets/168e2217-3f96-4585-9b61-ba1a05195723" />

