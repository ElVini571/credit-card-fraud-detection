
# ==================================================
# PROJETO DETECÇÃO DE FRAUDES BANCÁRIAS - ANALISE EXPLORATORIA DE DADOS
# ==================================================

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ETAPA 1 - PREPARAR OS CAMINHOS

arquivo = Path(
    "data/raw/Base de Dados - Projeto Integrador (1).xlsx"
)

pasta = Path("reports")
graficos = pasta / "figures"

graficos.mkdir(parents=True, exist_ok=True)

# ETAPA 2 - CARREGAR A BASE

df = pd.read_excel(
    arquivo,
    sheet_name="credit_card_fraud_2026"
)

# Remover linhas e colunas totalmente vazias
df = df.dropna(how="all").dropna(axis=1, how="all")

# Confirmar o formato das principais variaveis
df["is_fraud"] = df["is_fraud"].astype(int)
df["amount_usd"] = pd.to_numeric(df["amount_usd"])
df["time_of_day_hour"] = pd.to_numeric(
    df["time_of_day_hour"]
)

print("Base carregada:", df.shape)

# ETAPA 3 - CRIAR UMA FUNCAO DE RESUMO

def resumir_fraudes(coluna):
    tabela = (
        df.groupby(coluna)["is_fraud"]
        .agg(
            total="count",
            fraudes="sum",
            taxa="mean"
        )
        .reset_index()
    )

    # Transformar a taxa em porcentagem
    tabela["taxa_pct"] = (
        tabela["taxa"] * 100
    ).round(2)

    return tabela.drop(columns=["taxa"])


# ETAPA 4 - COMPARAR CATEGORIAS

categorias = resumir_fraudes(
    "merchant_category"
)

categorias = categorias.sort_values(
    "taxa_pct", ascending=False
)

print("\nFRAUDES POR CATEGORIA:")
print(categorias.to_string(index=False))

categorias.to_csv(
    pasta / "fraudes_por_categoria.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# Grafico de barras por categoria

top_categorias = categorias.head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    top_categorias["merchant_category"].astype(str),
    top_categorias["taxa_pct"],
    color="#2B6F9B"
)

plt.gca().invert_yaxis()
plt.title("Taxa de fraude por categoria")
plt.xlabel("Taxa de fraude (%)")
plt.ylabel("Categoria do estabelecimento")
plt.tight_layout()

plt.savefig(
    graficos / "fraudes_por_categoria.png",
    dpi=300
)
plt.close()


# ETAPA 5 - INVESTIGAR OS HORARIOS

horarios = resumir_fraudes(
    "time_of_day_hour"
).sort_values("time_of_day_hour")

horarios.to_csv(
    pasta / "fraudes_por_horario.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

plt.figure(figsize=(10, 5))

plt.plot(
    horarios["time_of_day_hour"],
    horarios["taxa_pct"],
    marker="o",
    color="#2B6F9B"
)

plt.title("Taxa de fraude por hora do dia")
plt.xlabel("Hora do dia")
plt.ylabel("Taxa de fraude (%)")
plt.xticks(range(0, 24, 2))
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    graficos / "fraudes_por_horario.png",
    dpi=300
)
plt.close()


# ETAPA 6 - INVESTIGAR VALORES MONETARIOS

# Usar ate o percentil 99 apenas na visualizacao
limite = df["amount_usd"].quantile(0.99)

dados_grafico = df[
    df["amount_usd"].between(0, limite)
]

legitimas = dados_grafico[
    dados_grafico["is_fraud"] == 0
]["amount_usd"]

fraudes = dados_grafico[
    dados_grafico["is_fraud"] == 1
]["amount_usd"]

bins = np.linspace(0, max(limite, 1), 31)

plt.figure(figsize=(10, 5))

plt.hist(
    legitimas,
    bins=bins,
    alpha=0.5,
    density=True,
    label="Legitimas"
)

plt.hist(
    fraudes,
    bins=bins,
    alpha=0.5,
    density=True,
    label="Fraudulentas"
)

plt.title("Distribuicao dos valores das transacoes")
plt.xlabel("Valor da transacao (USD)")
plt.ylabel("Densidade normalizada")
plt.legend()
plt.tight_layout()

plt.savefig(
    graficos / "distribuicao_valores.png",
    dpi=300
)
plt.close()


# ETAPA 7 - OUTRAS COMPARACOES

# Comparacao por canal de pagamento
canais = resumir_fraudes("channel")

canais.to_csv(
    pasta / "fraudes_por_canal.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# Comparacao por metodo de autenticacao
autenticacao = resumir_fraudes("auth_method")

autenticacao.to_csv(
    pasta / "fraudes_por_autenticacao.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("\nANALISE EXPLORATORIA CONCLUIDA!")
print("Graficos salvos em reports/figures")
print("Tabelas CSV salvas em reports")
