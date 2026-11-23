from pathlib import Path
import numpy as np
import pandas as pd

# --- Parte 1: Carregar e juntar ---

def carregar(pasta):
    pasta = Path(pasta)
    vendas = pd.read_csv(pasta / "vendas.csv", parse_dates=["data"])
    clientes = pd.read_csv(pasta / "clientes.csv", parse_dates=["data_registo"])
    produtos = pd.read_csv(pasta / "produtos.csv")
    return vendas, clientes, produtos


def juntar(vendas, clientes, produtos):
    df = (
        vendas
        .merge(
            clientes[["cliente_id", "tipo", "ilha"]],
            on="cliente_id",
            how="left",
        )
        .merge(
            produtos[["produto_id", "nome", "categoria"]],
            on="produto_id",
            how="left",
        )
    )
    df["total"] = df["quantidade"] * df["preco_unitario"]
    return df

   # --- Parte 2: Faturação mensal e top de produtos ---

def faturacao_mensal_por_ilha(df):
    dados = df.copy()
    dados["mes"] = dados["data"].dt.strftime("%Y-%m")
    return dados.pivot_table(
        index="mes",
        columns="ilha",
        values="total",
        aggfunc="sum",
        fill_value=0,
    )


def top_produtos(df, n):
    return (
        df.groupby("nome")["total"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )

# --- Parte 3: Quotas e desconto ---

def quota_por_tipo(df):
    por_tipo = df.groupby("tipo")["total"].sum()
    return ((por_tipo / df["total"].sum()) * 100).round(1)


def aplicar_desconto(df):
    df = df.copy()
    df["total_com_desconto"] = np.where(
        df["quantidade"] >= 20,
        df["total"] * 0.95,
        df["total"],
    )
    return df
