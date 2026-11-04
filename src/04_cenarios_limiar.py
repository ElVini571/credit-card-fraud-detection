
# ================================================
# PROJETO DETECÇÃO DE FRAUDES BANCÁRIAS - ANALISE DE LIMIARES
# ================================================

from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score
)

# ETAPA 1 - CARREGAR AS PREVISOES DE VALIDACAO

arquivo = Path("reports/predicoes_validacao.csv")

df = pd.read_csv(arquivo, sep=";")

# Respostas reais
y_real = df["classe_real"].astype(int)

# Valores estimados pelo modelo
probabilidades = df["probabilidade_fraude"].astype(float)

# ETAPA 2 - TESTAR DIFERENTES LIMIARES

resultados = []

for numero in range(5, 100, 5):

    limiar = numero / 100

    # Converter estimativas em alertas (0 ou 1)
    alertas = (probabilidades >= limiar).astype(int)

    # Calcular as metricas
    precisao = precision_score(
        y_real, alertas, zero_division=0
    )

    recall = recall_score(
        y_real, alertas, zero_division=0
    )

    f1 = f1_score(
        y_real, alertas, zero_division=0
    )

    # Matriz de confusao
    vn, fp, fn, vp = confusion_matrix(
        y_real, alertas, labels=[0, 1]
    ).ravel()

    resultados.append({
        "limiar": limiar,
        "precisao": precisao,
        "recall": recall,
        "f1": f1,
        "VP": int(vp),
        "FP": int(fp),
        "FN": int(fn),
        "VN": int(vn)
    })

# ETAPA 3 - ORGANIZAR RESULTADOS

tabela = pd.DataFrame(resultados)

tabela = tabela.sort_values("limiar")

Path("reports").mkdir(exist_ok=True)

tabela.to_csv(
    "reports/cenarios_limiares_validacao.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# ETAPA 4 - SELECIONAR O MELHOR F1

# Em caso de empate, priorizar maior precisao.
ranking = tabela.sort_values(
    ["f1", "precisao", "limiar"],
    ascending=[False, False, False]
)

melhor = ranking.iloc[0]

print("\nCOMPARACAO DOS LIMIARES:")
print(
    tabela[["limiar", "precisao", "recall", "f1"]]
    .round(4)
    .to_string(index=False)
)

print("\nMELHOR LIMIAR NA VALIDACAO:")
print("Limiar:", round(melhor["limiar"], 2))
print("Precisao:", round(melhor["precisao"], 4))
print("Recall:", round(melhor["recall"], 4))
print("F1-score:", round(melhor["f1"], 4))

print("\nMATRIZ DE CONFUSAO - VALIDACAO:")
print("Verdadeiros positivos:", int(melhor["VP"]))
print("Falsos positivos:", int(melhor["FP"]))
print("Falsos negativos:", int(melhor["FN"]))
print("Verdadeiros negativos:", int(melhor["VN"]))

# ETAPA 5 - SALVAR A ESCOLHA

escolha = {
    "limiar": float(melhor["limiar"]),
    "criterio": "maior F1 na validacao",
    "precisao_validacao": float(melhor["precisao"]),
    "recall_validacao": float(melhor["recall"]),
    "f1_validacao": float(melhor["f1"])
}

with open(
    "reports/limiar_selecionado.json",
    "w",
    encoding="utf-8"
) as arquivo_json:
    json.dump(escolha, arquivo_json, indent=4)

# ETAPA 6 - PRODUZIR GRAFICO

Path("reports/figures").mkdir(
    parents=True, exist_ok=True
)

plt.figure(figsize=(10, 6))

plt.plot(
    tabela["limiar"],
    tabela["precisao"],
    marker="o",
    label="Precisao"
)

plt.plot(
    tabela["limiar"],
    tabela["recall"],
    marker="o",
    label="Recall"
)

plt.plot(
    tabela["limiar"],
    tabela["f1"],
    marker="o",
    label="F1-score"
)

plt.axvline(
    melhor["limiar"],
    color="gray",
    linestyle="--",
    label="Limiar selecionado"
)

plt.title("Metricas por limiar - Validacao")
plt.xlabel("Limiar de decisao")
plt.ylabel("Valor da metrica")
plt.ylim(0, 1)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    "reports/figures/metricas_por_limiar.png",
    dpi=300
)

plt.close()

print("\nANALISE DOS LIMIARES CONCLUIDA!")
print("Resultados e grafico salvos.")
print("O conjunto de teste permanece reservado.")
