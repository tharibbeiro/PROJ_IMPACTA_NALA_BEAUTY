# 💅 Nala Beauty - Projeto Acadêmico

Projeto de faculdade de dados/BI: e-commerce fictício de maquiagem e produtos
de beleza, com 3 camadas — banco de dados, back-end e front-end.

## Arquitetura

```
SQL Server (dbo.*)  →  Python (backend/processar_metricas.py)  →  SQL Server (analytics.*)  →  Power BI
   dado bruto              aplica regras de negócio                 dado tratado              dashboard
```

## Estrutura

```
sql server/
├── 01_criar_tabelas.sql      
└── 02_inserir_dados.sql      
backend/
├── processar_metricas.py     
├── requirements.txt
└── .env.example             
data/
└── gerar_dados.py            
dashboard/
├── Nala Beauty BI.pbix       -- dashboard Power BI
└── logo_nala_beauty.png


## Como rodar

1. **Banco de dados**:
   Foi criado o banco de dados Ecommerce_Nala_Beauty, executado o script `sql/01_criar_tabelas.sql` que criou as tabelas bases e depois foi executado `sql/02_inserir_dados.sql` que inseriu os dados fícticios.
2. **Back-end**:
   Refinamento e tratamentos dos dados do ecommerce para calcular as metrícas de vendas utilizando python, e gravando nos schemas `analytics`.  
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
   
   Painel foi criado utilizando as métricas cálculadas, e o resultado final ficou dessa forma, para que possa ser feito acompanhamento e monitoramento das vendas:
   
   <img width="1317" height="737" alt="image" src="https://github.com/user-attachments/assets/168e2217-3f96-4585-9b61-ba1a05195723" />

