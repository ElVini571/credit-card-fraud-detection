
import pandas as pd
import matplotlib.pyplot as plt

# Localização da planilha
arquivo = "data/raw/Base de Dados - Projeto Integrador (1).xlsx"

# Carregar os dados do Excel
df = pd.read_excel(
    arquivo,
    sheet_name="credit_card_fraud_2026"
)

# Remover linhas e colunas inteiramente vazias
df = df.dropna(how="all").dropna(axis=1, how="all")

# Conferir a quantidade de registros e colunas
print("Linhas e colunas:", df.shape)

# Verificar dados ausentes
print("Valores ausentes:", df.isna().sum().sum())

# Verificar identificadores duplicados
print("IDs duplicados:", df["transaction_id"].duplicated().sum())

# Contar transações legítimas e fraudulentas
print("Distribuição de fraudes:")
print(df["is_fraud"].value_counts())


from pathlib import Path

# Criar a pasta onde os gráficos serão salvos
Path("reports/figures").mkdir(parents=True, exist_ok=True)

# Contar cada tipo de transação
contagem = df["is_fraud"].value_counts()

legitimas = contagem.get(0, 0)
fraudes = contagem.get(1, 0)

# Criar a figura
plt.figure(figsize=(9, 5))

barras = plt.bar(
    ["Legítimas", "Fraudulentas"],
    [legitimas, fraudes],
    color=["#27836F", "#D97757"]
)

# Colocar a quantidade em cima de cada barra
plt.bar_label(barras, padding=3)

# Adicionar título e identificação dos eixos
plt.title("Distribuição das transações")
plt.xlabel("Classificação")
plt.ylabel("Quantidade de transações")

# Ajustar o gráfico
plt.tight_layout()

# Salvar a imagem
plt.savefig(
    "reports/figures/distribuicao_classes.png",
    dpi=300
)

# Mostrar o gráfico na tela
plt.show()
