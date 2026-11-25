"""Lab 5 · Transformar (limpar) as vendas com funções puras.

Função pura = não altera o que recebe e devolve sempre o mesmo para a mesma
entrada. Testa com:
    pytest tests/test_etl_lab5.py -v
"""

import unicodedata

import pandas as pd

ILHAS_VALIDAS = ["Santiago", "São Vicente", "Sal", "Boa Vista", "Fogo", "Santo Antão"]

# abreviaturas que aparecem nos dados (chave já "achatada")
_ALIASES = {
    "stgo": "Santiago",
    "sv": "São Vicente",
    "svicente": "São Vicente",
    "boavista": "Boa Vista",
    "santao": "Santo Antão",
}


def _achatar(texto):
    """(VEM PRONTA) 'S. Vicente ' -> 'svicente' (minúsculas, sem acentos,
    só letras e números)."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(ch for ch in sem_acentos.lower() if ch.isalnum())


_CANON = {_achatar(i): i for i in ILHAS_VALIDAS} | _ALIASES


def normalizar_ilha(texto):
    """'  SAO vicente' -> 'São Vicente'. Ilha não servida, vazia ou None -> None.
    Dica: _CANON.get(_achatar(...))"""
    if texto is None or pd.isna(texto):
        return None

    chave = _achatar(str(texto))
    if not chave:
        return None

    return _CANON.get(chave)


def normalizar_data(texto):
    """Aceita '2025-03-01' e '01/03/2025'. Devolve pd.Timestamp; data
    impossível ou vazia -> pd.NaT. Dica: pd.to_datetime(..., format=..., errors="coerce")"""
    if texto is None or pd.isna(texto):
        return pd.NaT

    limpo = str(texto).strip()
    if not limpo:
        return pd.NaT

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        dt = pd.to_datetime(limpo, format=fmt, errors="coerce")
        if not pd.isna(dt):
            return dt

    return pd.NaT


def limpar_numero(serie):
    """(VEM PRONTA) '12 un' -> 12.0, '1250 CVE' -> 1250.0, '' -> NaN.
    A expressão regular apanha o primeiro número (com casas decimais opcionais)."""
    return (serie.astype("string")
                 .str.extract(r"(\d+(?:[.,]\d+)?)", expand=False)
                 .str.replace(",", ".", regex=False)
                 .astype(float))


def remover_duplicados(df):
    """Remove linhas com venda_id repetido (fica a primeira)."""
    return df.drop_duplicates(subset=["venda_id"], keep="first")


def limpar_vendas(df):
    """Junta tudo. NÃO altera o df original (usa .assign ou .copy()).
    Passos:
      1. remover duplicados
      2. normalizar ilha e data; limpar quantidade e preco_unitario
      3. remover linhas onde algum destes quatro ficou vazio
      4. quantidade e preco_unitario como int
    """
    # 1. Remover duplicados mantendo a primeira ocorrência sem mutar df
    base = remover_duplicados(df).copy()

    # 2. Normalizar ilha e data; limpar quantidade e preco_unitario        ...

    limpo = base.assign(
        ilha=base["ilha"].apply(normalizar_ilha),
        data=base["data"].apply(normalizar_data),
        quantidade=limpar_numero(base["quantidade"]),
        preco_unitario=limpar_numero(base["preco_unitario"]),
    )

    # 3. Remover linhas onde algum destes quatro ficou vazio (None, pd.NaT ou pd.NA)
    obrigatorias = ["ilha", "data", "quantidade", "preco_unitario"]
    filtrado = limpo.dropna(subset=obrigatorias)

    # 4. Converter quantidade e preco_unitario para int
    return filtrado.assign(
        quantidade=filtrado["quantidade"].astype(int),
        preco_unitario=filtrado["preco_unitario"].astype(int),
    )


if __name__ == "__main__":
    print(pd.__version__)
    