/* =========================================================
   E-commerce Fictício - Criação das tabelas (SQL Server)
   Modelo: 3 dimensões (Categorias, Produtos, Clientes)
           + 2 tabelas transacionais (Pedidos, ItensPedido)
   ========================================================= */

IF DB_ID('Ecommerce_Nala_Beauty') IS NULL
BEGIN
    CREATE DATABASE Ecommerce_Nala_Beauty;
END
GO

USE Ecommerce_Nala_Beauty;
GO

-- Limpa tabelas se já existirem (permite rodar o script de novo sem erro)
IF OBJECT_ID('dbo.ItensPedido', 'U') IS NOT NULL DROP TABLE dbo.ItensPedido;
IF OBJECT_ID('dbo.Pedidos', 'U') IS NOT NULL DROP TABLE dbo.Pedidos;
IF OBJECT_ID('dbo.Produtos', 'U') IS NOT NULL DROP TABLE dbo.Produtos;
IF OBJECT_ID('dbo.Clientes', 'U') IS NOT NULL DROP TABLE dbo.Clientes;
IF OBJECT_ID('dbo.Categorias', 'U') IS NOT NULL DROP TABLE dbo.Categorias;
GO

CREATE TABLE dbo.Categorias (
    CategoriaID   INT IDENTITY(1,1) PRIMARY KEY,
    Nome          NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE dbo.Produtos (
    ProdutoID     INT IDENTITY(1,1) PRIMARY KEY,
    Nome          NVARCHAR(150) NOT NULL,
    CategoriaID   INT NOT NULL,
    Preco         DECIMAL(10,2) NOT NULL,
    Estoque       INT NOT NULL DEFAULT 0,
    CONSTRAINT FK_Produtos_Categorias FOREIGN KEY (CategoriaID)
        REFERENCES dbo.Categorias(CategoriaID)
);
GO

CREATE TABLE dbo.Clientes (
    ClienteID     INT IDENTITY(1,1) PRIMARY KEY,
    Nome          NVARCHAR(150) NOT NULL,
    Email         NVARCHAR(150) NOT NULL,
    Cidade        NVARCHAR(100) NOT NULL,
    Estado        CHAR(2) NOT NULL,
    DataCadastro  DATE NOT NULL
);
GO

CREATE TABLE dbo.Pedidos (
    PedidoID      INT IDENTITY(1,1) PRIMARY KEY,
    ClienteID     INT NOT NULL,
    DataPedido    DATE NOT NULL,
    Status        NVARCHAR(20) NOT NULL, -- Pendente, Enviado, Entregue, Cancelado
    CONSTRAINT FK_Pedidos_Clientes FOREIGN KEY (ClienteID)
        REFERENCES dbo.Clientes(ClienteID)
);
GO

CREATE TABLE dbo.ItensPedido (
    ItemID          INT IDENTITY(1,1) PRIMARY KEY,
    PedidoID        INT NOT NULL,
    ProdutoID       INT NOT NULL,
    Quantidade      INT NOT NULL,
    PrecoUnitario   DECIMAL(10,2) NOT NULL,
    CONSTRAINT FK_ItensPedido_Pedidos FOREIGN KEY (PedidoID)
        REFERENCES dbo.Pedidos(PedidoID),
    CONSTRAINT FK_ItensPedido_Produtos FOREIGN KEY (ProdutoID)
        REFERENCES dbo.Produtos(ProdutoID)
);
GO

-- View de apoio: pedidos com valor total já calculado (útil para o dashboard)
CREATE OR ALTER VIEW dbo.vw_PedidosResumo AS
SELECT
    p.PedidoID,
    c.Nome        AS Cliente,
    c.Cidade,
    c.Estado,
    p.DataPedido,
    p.Status,
    SUM(ip.Quantidade * ip.PrecoUnitario) AS ValorTotal
FROM dbo.Pedidos p
JOIN dbo.Clientes c ON c.ClienteID = p.ClienteID
JOIN dbo.ItensPedido ip ON ip.PedidoID = p.PedidoID
GROUP BY p.PedidoID, c.Nome, c.Cidade, c.Estado, p.DataPedido, p.Status;
GO
