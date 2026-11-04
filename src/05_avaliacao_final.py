
# =================================================
# UFMS - PROJETO DE DETECCAO DE FRAUDES
# ETAPA 7 - AVALIACAO FINAL DO MODELO
# =================================================

import json
from pathlib import Path

import joblib
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    average_precision_score,
    precision_recall_curve
)

# ETAPA 1 - LOCALIZAR OS ARQUIVOS

base = Path(
    "data/raw/Base de Dados - Projeto Integrador (1).xlsx"
)

arquivo_modelo = Path(
    "models/pipeline_fraudes.joblib"
)

arquivo_limiar = Path(
    "reports/limiar_selecionado.json"
)

# Verificar se os arquivos existem

for arquivo in [base, arquivo_modelo, arquivo_limiar]:
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {arquivo}"
        )

# Criar pastas de resultados

Path("reports/figures").mkdir(
    parents=True, exist_ok=True
)

# ETAPA 2 - CARREGAR A BASE

df = pd.read_excel(
    base,
    sheet_name="credit_card_fraud_2026"
)

df = df.dropna(how="all").dropna(
    axis=1, how="all"
)

# Conferir que continuamos com a base original
if df.shape != (20000, 26):
    raise ValueError(
        "A base mudou desde o treinamento. "
        "Revise os arquivos antes de avaliar."
    )

print("Base carregada:", df.shape)

# ETAPA 3 - RECONSTRUIR A DIVISAO ORIGINAL

X = df.drop(columns=[
    "is_fraud",
    "transaction_id",
    "is_ai_generated_scam_attempt"
])

y = df["is_fraud"].astype(int)

# Mesmos parametros do treinamento anterior
X_dev, X_teste, y_dev, y_teste = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

print("Transacoes de teste:", len(X_teste))

# ETAPA 4 - CARREGAR O MODELO TREINADO

modelo = joblib.load(arquivo_modelo)

# Carregar limiar selecionado na validacao
with open(
    arquivo_limiar,
    "r",
    encoding="utf-8"
) as f:
    configuracao = json.load(f)

limiar = float(configuracao["limiar"])

if not 0 <= limiar <= 1:
    raise ValueError("Limiar invalido.")

print("Limiar selecionado:", limiar)

# ETAPA 5 - FAZER PREVISOES NO TESTE

# Obter os valores estimados de fraude
probabilidades = modelo.predict_proba(
    X_teste
)[:, 1]

# Converter em alertas conforme o limiar
previsoes = (
    probabilidades >= limiar
).astype(int)

# ETAPA 6 - CALCULAR AS METRICAS

acuracia = accuracy_score(
    y_teste, previsoes
)

precisao = precision_score(
    y_teste, previsoes, zero_division=0
)

recall = recall_score(
    y_teste, previsoes, zero_division=0
)

f1 = f1_score(
    y_teste, previsoes, zero_division=0
)

ap = average_precision_score(
    y_teste, probabilidades
)

# ETAPA 7 - MATRIZ DE CONFUSAO

matriz = confusion_matrix(
    y_teste, previsoes, labels=[0, 1]
)

vn, fp, fn, vp = matriz.ravel()

print("\nRESULTADOS FINAIS DO TESTE")
print("-" * 35)

print(f"Acuracia: {acuracia:.4f}")
print(f"Precisao: {precisao:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-score: {f1:.4f}")
print(f"Average Precision: {ap:.4f}")

print("\nMATRIZ DE CONFUSAO")
print("Verdadeiros positivos:", vp)
print("Falsos positivos:", fp)
print("Falsos negativos:", fn)
print("Verdadeiros negativos:", vn)

# ETAPA 8 - SALVAR RESULTADOS

resultados = {
    "modelo": "Regressao Logistica",
    "limiar": limiar,
    "total_teste": int(len(y_teste)),
    "acuracia": float(acuracia),
    "precisao": float(precisao),
    "recall": float(recall),
    "f1_score": float(f1),
    "average_precision": float(ap),
    "verdadeiros_positivos": int(vp),
    "falsos_positivos": int(fp),
    "falsos_negativos": int(fn),
    "verdadeiros_negativos": int(vn)
}

with open(
    "reports/metricas_modelo.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        resultados,
        f,
        indent=4,
        ensure_ascii=False
    )

# Salvar as previsoes individuais

tabela = pd.DataFrame({
    "transaction_id": df.loc[
        X_teste.index, "transaction_id"
    ].to_numpy(),
    "amount_usd": df.loc[
        X_teste.index, "amount_usd"
    ].to_numpy(),
    "classe_real": y_teste.to_numpy(),
    "probabilidade_fraude": probabilidades,
    "alerta_modelo": previsoes
})

tabela.to_csv(
    "reports/predicoes_teste.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# ETAPA 9 - GRAFICO DA MATRIZ DE CONFUSAO

fig, ax = plt.subplots(figsize=(7, 6))

imagem = ax.imshow(
    matriz,
    cmap="Blues"
)

ax.set_xticks([0, 1])
ax.set_yticks([0, 1])

ax.set_xticklabels([
    "Legitima", "Fraude"
])

ax.set_yticklabels([
    "Legitima", "Fraude"
])

ax.set_xlabel("Classificacao prevista")
ax.set_ylabel("Classificacao real")
ax.set_title("Matriz de Confusao - Teste")

for i in range(2):
    for j in range(2):
        valor = matriz[i, j]

        ax.text(
            j, i, str(valor),
            ha="center",
            va="center",
            color=(
                "white"
                if valor > matriz.max() / 2
                else "black"
            ),
            fontsize=14
        )

fig.colorbar(imagem, ax=ax)
plt.tight_layout()

plt.savefig(
    "reports/figures/matriz_confusao_teste.png",
    dpi=300
)

plt.close()

# ETAPA 10 - CURVA PRECISAO-RECALL

precisoes, recalls, _ = precision_recall_curve(
    y_teste,
    probabilidades
)

plt.figure(figsize=(8, 6))

plt.plot(
    recalls,
    precisoes,
    label=f"Modelo (AP = {ap:.3f})"
)

# Referencia correspondente a prevalencia no teste
prevalencia = y_teste.mean()

plt.axhline(
    prevalencia,
    color="gray",
    linestyle="--",
    label="Prevalencia no teste"
)

plt.xlabel("Recall")
plt.ylabel("Precisao")
plt.title("Curva Precisao-Recall - Teste")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    "reports/figures/curva_precisao_recall.png",
    dpi=300
)

plt.close()

print("\nAVALIACAO FINAL CONCLUIDA!")
print("Resultados salvos em reports/")
print("Graficos salvos em reports/figures/")
