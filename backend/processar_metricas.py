"""
Processamento de métricas do e-commerce Nala Beauty.

Métricas geradas (schema analytics):
    - FaturamentoMensal        (AnoMes, Faturamento)
    - FaturamentoPorCategoria  (Categoria, Faturamento, QtdItensVendidos)
    - TopProdutos              (Produto, Categoria, Faturamento, QtdVendida)
    - TicketMedioPorCliente    (ClienteID, Cliente, QtdPedidos, TicketMedio)
    - PedidosPorStatus         (Status, QtdPedidos)
    - ClientesRecorrentes      (ClienteID, Cliente, QtdPedidos) — top 10


Uso:
    python processar_metricas.py
"""

import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

SERVER = os.environ["SQL_SERVER"]              
DATABASE = os.environ.get("SQL_DATABASE", "Ecommerce_Nala_Beauty")
DRIVER = os.environ.get("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
TRUSTED_CONNECTION = os.environ.get("SQL_TRUSTED_CONNECTION", "yes")
USERNAME = os.environ.get("SQL_USERNAME", "")
PASSWORD = os.environ.get("SQL_PASSWORD", "")


def get_engine():
    """Monta a connection string. Suporta autenticação Windows ou SQL Server."""
    driver_fmt = DRIVER.replace(" ", "+")
    if TRUSTED_CONNECTION.lower() == "yes":
        conn_str = (
            f"mssql+pyodbc://{SERVER}/{DATABASE}"
            f"?driver={driver_fmt}&trusted_connection=yes"
        )
    else:
        conn_str = (
            f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}"
            f"?driver={driver_fmt}"
        )
    return create_engine(conn_str)


def criar_schema_analytics(engine):
    with engine.begin() as conn:
        conn.execute(text(
            "IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'analytics') "
            "EXEC('CREATE SCHEMA analytics')"
        ))


def carregar_dados_brutos(engine):
    clientes = pd.read_sql("SELECT * FROM dbo.Clientes", engine)
    produtos = pd.read_sql("SELECT * FROM dbo.Produtos", engine)
    categorias = pd.read_sql("SELECT * FROM dbo.Categorias", engine)
    pedidos = pd.read_sql("SELECT * FROM dbo.Pedidos", engine)
    itens = pd.read_sql("SELECT * FROM dbo.ItensPedido", engine)
    return clientes, produtos, categorias, pedidos, itens


def montar_base_unificada(clientes, produtos, categorias, pedidos, itens):
    """Junta as 5 tabelas em uma base única, já com nomes de coluna sem ambiguidade."""
    clientes = clientes.rename(columns={"Nome": "Cliente"})
    produtos = produtos.rename(columns={"Nome": "Produto"})
    categorias = categorias.rename(columns={"Nome": "Categoria"})

    itens = itens.copy()
    itens["ValorItem"] = itens["Quantidade"] * itens["PrecoUnitario"]

    base = itens.merge(pedidos, on="PedidoID")
    base = base.merge(produtos[["ProdutoID", "Produto", "CategoriaID"]], on="ProdutoID")
    base = base.merge(categorias[["CategoriaID", "Categoria"]], on="CategoriaID")
    base = base.merge(clientes[["ClienteID", "Cliente"]], on="ClienteID")
    base["DataPedido"] = pd.to_datetime(base["DataPedido"])
    base["AnoMes"] = base["DataPedido"].dt.to_period("M").astype(str)
    return base


def calcular_metricas(base: pd.DataFrame, pedidos: pd.DataFrame) -> dict:
    metricas = {}

    # 1) Faturamento mensal
    metricas["FaturamentoMensal"] = (
        base.groupby("AnoMes")["ValorItem"]
        .sum()
        .reset_index()
        .rename(columns={"ValorItem": "Faturamento"})
        .sort_values("AnoMes")
        .reset_index(drop=True)
    )

    # 2) Faturamento por categoria
    metricas["FaturamentoPorCategoria"] = (
        base.groupby("Categoria")
        .agg(Faturamento=("ValorItem", "sum"), QtdItensVendidos=("Quantidade", "sum"))
        .reset_index()
        .sort_values("Faturamento", ascending=False)
        .reset_index(drop=True)
    )

    # 3) Top 10 produtos por faturamento
    metricas["TopProdutos"] = (
        base.groupby(["Produto", "Categoria"])
        .agg(Faturamento=("ValorItem", "sum"), QtdVendida=("Quantidade", "sum"))
        .reset_index()
        .sort_values("Faturamento", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    # 4) Ticket médio por cliente (considera só pedidos com itens)
    valor_por_pedido = base.groupby(["PedidoID", "ClienteID", "Cliente"])["ValorItem"].sum().reset_index()
    metricas["TicketMedioPorCliente"] = (
        valor_por_pedido.groupby(["ClienteID", "Cliente"])
        .agg(QtdPedidos=("PedidoID", "nunique"), TicketMedio=("ValorItem", "mean"))
        .reset_index()
        .sort_values("TicketMedio", ascending=False)
        .reset_index(drop=True)
    )

    # 5) Pedidos por status
    metricas["PedidosPorStatus"] = (
        pedidos.groupby("Status")
        .size()
        .reset_index(name="QtdPedidos")
        .sort_values("QtdPedidos", ascending=False)
        .reset_index(drop=True)
    )

    # 6) Top 10 clientes recorrentes (2+ pedidos), ordenado por qtd. de pedidos
    metricas["ClientesRecorrentes"] = (
        metricas["TicketMedioPorCliente"][metricas["TicketMedioPorCliente"]["QtdPedidos"] >= 2]
        [["ClienteID", "Cliente", "QtdPedidos"]]
        .sort_values("QtdPedidos", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    return metricas


def gravar_metricas(engine, metricas: dict):
    for nome_tabela, df in metricas.items():
        df.to_sql(
            nome_tabela,
            engine,
            schema="analytics",
            if_exists="replace",
            index=False,
        )
        print(f"  -> analytics.{nome_tabela}: {len(df)} linhas gravadas")


def main():
    engine = get_engine()
    print(f"Conectado em {SERVER}/{DATABASE}")

    criar_schema_analytics(engine)

    clientes, produtos, categorias, pedidos, itens = carregar_dados_brutos(engine)
    print(f"Dados brutos carregados: {len(pedidos)} pedidos, {len(itens)} itens")

    base = montar_base_unificada(clientes, produtos, categorias, pedidos, itens)
    metricas = calcular_metricas(base, pedidos)

    print("Gravando métricas em analytics.*:")
    gravar_metricas(engine, metricas)

    print("\nConcluído. No Power BI, conecte no SQL Server e use as tabelas do schema 'analytics'.")


if __name__ == "__main__":
    main()