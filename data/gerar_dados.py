"""
Gera dados fictícios do e-commerce Nala Beauty (maquiagem e produtos de
beleza) e escreve um script T-SQL (02_inserir_dados.sql) pronto para rodar
no SQL Server logo após o 01_criar_tabelas.sql.

Uso:
    python gerar_dados.py
"""

import random
from datetime import date, timedelta

from faker import Faker

fake = Faker("pt_BR")
random.seed(42)
Faker.seed(42)

N_CLIENTES = 100
N_PRODUTOS_POR_CATEGORIA = 8
N_PEDIDOS = 300
STATUS_POSSIVEIS = ["Pendente", "Enviado", "Entregue", "Cancelado"]

CATEGORIAS = [
    "Maquiagem para Rosto", "Maquiagem para Olhos", "Maquiagem para Lábios",
    "Skincare", "Cabelo", "Corpo e Banho", "Perfumaria", "Unhas",
]

PRODUTOS_POR_CATEGORIA = {
    "Maquiagem para Rosto": ["Base Líquida Matte", "Corretivo de Alta Cobertura", "Pó Compacto Translúcido",
                             "Blush em Bastão", "Iluminador Facial", "Primer Facial", "Contorno em Pó",
                             "BB Cream FPS 30"],
    "Maquiagem para Olhos": ["Paleta de Sombras 12 Cores", "Máscara de Cílios Volume", "Delineador em Gel",
                              "Lápis de Olho Preto", "Sobrancelha em Gel", "Primer para Pálpebras",
                              "Cílios Postiços", "Delineador Líquido"],
    "Maquiagem para Lábios": ["Batom Matte Vermelho", "Gloss Labial Hidratante", "Lápis de Boca",
                               "Batom Líquido Nude", "Balm Labial com Cor", "Tinta Labial de Longa Duração",
                               "Batom Cremoso Rosa", "Kit Mini Batons"],
    "Skincare": ["Sérum de Vitamina C", "Protetor Solar Facial FPS 60", "Água Micelar", "Ácido Hialurônico",
                 "Creme Hidratante Facial", "Esfoliante Facial", "Máscara de Argila", "Gel de Limpeza Facial"],
    "Cabelo": ["Shampoo Hidratante", "Condicionador Reparador", "Máscara Capilar Nutritiva",
               "Óleo Finalizador", "Leave-in Anticrespo", "Spray Protetor Térmico",
               "Ampola de Reconstrução", "Creme para Pentear"],
    "Corpo e Banho": ["Hidratante Corporal", "Óleo Corporal Perfumado", "Sabonete Líquido Cremoso",
                       "Esfoliante Corporal", "Creme para Mãos", "Desodorante Roll-on",
                       "Loção Autobronzeadora", "Manteiga Corporal"],
    "Perfumaria": ["Perfume Floral 100ml", "Colônia Cítrica 75ml", "Perfume Amadeirado 50ml",
                    "Body Splash", "Perfume Doce Gourmand", "Água Perfumada Refrescante",
                    "Perfume Importado Feminino", "Miniatura de Perfume"],
    "Unhas": ["Esmalte Cremoso", "Base Fortalecedora", "Top Coat Brilho Intenso", "Removedor sem Acetona",
              "Óleo para Cutículas", "Esmalte em Gel", "Kit Manicure", "Adesivo Decorativo para Unhas"],
}


def sql_escape(texto: str) -> str:
    return texto.replace("'", "''")


def gerar_script():
    linhas = ["USE Ecommerce_Nala_Beauty;", "GO", ""]

    # ---------- Categorias ----------
    linhas.append("-- Categorias")
    linhas.append("INSERT INTO dbo.Categorias (Nome) VALUES")
    linhas.append(",\n".join(f"('{c}')" for c in CATEGORIAS) + ";")
    linhas.append("GO\n")

    # ---------- Produtos ----------
    linhas.append("-- Produtos")
    linhas.append("INSERT INTO dbo.Produtos (Nome, CategoriaID, Preco, Estoque) VALUES")
    produtos_valores = []
    produto_id_map = []  # guarda (categoria_index, nome) na ordem de inserção
    for cat_idx, categoria in enumerate(CATEGORIAS, start=1):
        for nome_produto in PRODUTOS_POR_CATEGORIA[categoria]:
            preco = round(random.uniform(9.90, 249.90), 2)
            estoque = random.randint(0, 200)
            produtos_valores.append(
                f"('{sql_escape(nome_produto)}', {cat_idx}, {preco}, {estoque})"
            )
            produto_id_map.append(nome_produto)
    linhas.append(",\n".join(produtos_valores) + ";")
    linhas.append("GO\n")
    total_produtos = len(produtos_valores)

    # ---------- Clientes ----------
    linhas.append("-- Clientes")
    linhas.append("INSERT INTO dbo.Clientes (Nome, Email, Cidade, Estado, DataCadastro) VALUES")
    clientes_valores = []
    for _ in range(N_CLIENTES):
        nome = fake.name()
        email = fake.unique.email()
        cidade = fake.city()
        estado = fake.estado_sigla()
        data_cadastro = fake.date_between(start_date="-2y", end_date="-1M")
        clientes_valores.append(
            f"('{sql_escape(nome)}', '{email}', '{sql_escape(cidade)}', '{estado}', '{data_cadastro.isoformat()}')"
        )
    linhas.append(",\n".join(clientes_valores) + ";")
    linhas.append("GO\n")

    # ---------- Pedidos + ItensPedido ----------
    # Pedidos e itens são gerados juntos para manter a integridade referencial
    # (cada pedido recebe de 1 a 4 itens de produtos aleatórios)
    linhas.append("-- Pedidos")
    linhas.append("INSERT INTO dbo.Pedidos (ClienteID, DataPedido, Status) VALUES")
    pedidos_valores = []
    itens_por_pedido = []  # lista de listas de (produto_id, quantidade, preco_unitario)

    for _ in range(N_PEDIDOS):
        cliente_id = random.randint(1, N_CLIENTES)
        data_pedido = fake.date_between(start_date="-1y", end_date="today")
        status = random.choices(STATUS_POSSIVEIS, weights=[0.15, 0.20, 0.55, 0.10])[0]
        pedidos_valores.append(f"({cliente_id}, '{data_pedido.isoformat()}', '{status}')")

        n_itens = random.randint(1, 4)
        itens = []
        for _ in range(n_itens):
            produto_id = random.randint(1, total_produtos)
            quantidade = random.randint(1, 3)
            preco_unitario = round(random.uniform(9.90, 249.90), 2)
            itens.append((produto_id, quantidade, preco_unitario))
        itens_por_pedido.append(itens)

    linhas.append(",\n".join(pedidos_valores) + ";")
    linhas.append("GO\n")

    linhas.append("-- ItensPedido")
    linhas.append("INSERT INTO dbo.ItensPedido (PedidoID, ProdutoID, Quantidade, PrecoUnitario) VALUES")
    itens_valores = []
    for pedido_id, itens in enumerate(itens_por_pedido, start=1):
        for produto_id, quantidade, preco_unitario in itens:
            itens_valores.append(f"({pedido_id}, {produto_id}, {quantidade}, {preco_unitario})")
    linhas.append(",\n".join(itens_valores) + ";")
    linhas.append("GO\n")

    return "\n".join(linhas)


if __name__ == "__main__":
    script = gerar_script()
    caminho_saida = "../sql/02_inserir_dados.sql"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"Script gerado em: {caminho_saida}")
