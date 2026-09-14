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
└── .env.example              -- copie para .env e configure sua conexão
data/
└── gerar_dados.py            -- gera o script 02_inserir_dados.sql
dashboard/
├── BI.pbix                   -- dashboard Power BI
└── logo_nala_beauty.png
docs/
└── roteiro_video.md          -- roteiro do vídeo de demonstração
```

## Como rodar

1. **Banco de dados**: rode `sql/01_criar_tabelas.sql` e depois
   `sql/02_inserir_dados.sql` no SQL Server (SSMS ou Azure Data Studio).
2. **Back-end**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env    # preencha com os dados da sua instância
   python processar_metricas.py
   ```
3. **Dashboard**: abra `dashboard/BI.pbix` no Power BI Desktop e atualize os
   dados (ele já está configurado para ler do schema `analytics`).

## Métricas calculadas (schema `analytics`)
- `FaturamentoMensal` — faturamento por mês
- `FaturamentoPorCategoria` — faturamento por categoria de produto
- `TopProdutos` — top 10 produtos por faturamento
- `TicketMedioPorCliente` — ticket médio e qtd. de pedidos por cliente
- `PedidosPorStatus` — quantidade de pedidos por status
- `ClientesRecorrentes` — top 10 clientes com 2+ pedidos
