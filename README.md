# Nala Beauty — E-commerce de Maquiagem e Beleza (Banco de Dados SQL Server)

Modelo simples de e-commerce com 5 tabelas: `Categorias`, `Produtos`, `Clientes`,
`Pedidos` e `ItensPedido`. Catálogo focado em maquiagem, skincare, cabelo,
perfumaria, corpo e unhas.

## Como subir no SQL Server (SSMS ou Azure Data Studio)

1. Abra o **01_criar_tabelas.sql** e execute (cria o banco `Ecommerce_Nala_Beauty` e as tabelas).
2. Abra o **02_inserir_dados.sql** e execute (popula com ~100 clientes, 64 produtos de beleza,
   300 pedidos e seus itens — tudo fictício, gerado com a biblioteca Faker).
3. Pronto — já dá pra consultar `dbo.vw_PedidosResumo` pra ver pedidos com valor total calculado.

## Estrutura

```
sql/
├── 01_criar_tabelas.sql      -- roda primeiro
└── 02_inserir_dados.sql      -- roda depois
backend/
├── processar_metricas.py     -- roda depois de popular o banco
├── requirements.txt
└── .env.example              -- copie para .env e preencha
data/
└── gerar_dados.py            -- script que gerou o 02_inserir_dados.sql
                                  (rode de novo se quiser outro volume/seed de dados)
```

## Modelo de dados

```
Categorias (1) ──< Produtos (N)
Clientes (1) ──< Pedidos (N) ──< ItensPedido (N) >── Produtos
```

## Camadas do projeto

1. **Banco de dados** (SQL Server): tabelas transacionais em `dbo.*` (Clientes,
   Produtos, Categorias, Pedidos, ItensPedido).
2. **Back-end** (`backend/processar_metricas.py`): conecta no SQL Server, calcula
   as métricas de negócio com pandas e grava o resultado em tabelas agregadas no
   schema `analytics.*` (FaturamentoMensal, FaturamentoPorCategoria, TopProdutos,
   TicketMedioPorCliente, PedidosPorStatus, ClientesRecorrentes).
3. **Front-end** (Power BI): conecta **nas tabelas do schema `analytics`**, nunca
   direto nas tabelas `dbo.*` — isso mantém a separação real entre back-end e
   front-end.

### Como rodar o back-end
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env    # edite com os dados da sua instância SQL Server
python processar_metricas.py
```

### Conectar o Power BI
No Power BI Desktop: **Obter Dados → SQL Server** → informe o servidor e o banco
`Ecommerce_Nala_Beauty` → selecione as tabelas do schema **analytics** (não use
o schema `dbo`).
