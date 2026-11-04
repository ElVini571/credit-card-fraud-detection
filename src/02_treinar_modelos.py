
# ===================================================
# PROJETO DETECÇÃO DE FRAUDES BANCÁRIAS - DETECCAO DE FRAUDES
# TREINAMENTO E COMPARACAO DE CLASSIFICADORES
# ===================================================

from pathlib import Path
import json
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

# ETAPA 1 - CARREGAR A BASE

arquivo = Path(
    "data/raw/Base de Dados - Projeto Integrador (1).xlsx"
)

df = pd.read_excel(
    arquivo,
    sheet_name="credit_card_fraud_2026"
)

df = df.dropna(how="all").dropna(axis=1, how="all")

print("Base carregada:", df.shape)

# ETAPA 2 - SEPARAR AS VARIAVEIS

# X contem as caracteristicas usadas para prever.
# y contem a resposta correta (fraude ou legitima).

colunas_excluidas = [
    "is_fraud",
    "transaction_id",
    "is_ai_generated_scam_attempt"
]

X = df.drop(columns=colunas_excluidas)
y = df["is_fraud"].astype(int)

# ETAPA 3 - DIVIDIR OS DADOS

# Primeiro reservamos 20% para o teste final.

X_dev, X_teste, y_dev, y_teste = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

# Agora dividimos os 80% restantes.
# 25% de 80% equivale a 20% da base completa.

X_treino, X_valid, y_treino, y_valid = train_test_split(
    X_dev,
    y_dev,
    test_size=0.25,
    stratify=y_dev,
    random_state=42
)

print("\nDivisao dos dados:")
print("Treinamento:", len(X_treino))
print("Validacao:", len(X_valid))
print("Teste reservado:", len(X_teste))

# ETAPA 4 - IDENTIFICAR TIPOS DE COLUNAS

colunas_numericas = X_treino.select_dtypes(
    include=["number", "bool"]
).columns.tolist()

colunas_categoricas = [
    coluna for coluna in X_treino.columns
    if coluna not in colunas_numericas
]

print("\nVariaveis numericas:", len(colunas_numericas))
print("Variaveis categoricas:", len(colunas_categoricas))

# ETAPA 5 - PREPARAR O PRE-PROCESSAMENTO

preprocessador = ColumnTransformer([
    (
        "numericas",
        Pipeline([
            ("nulos", SimpleImputer(strategy="median")),
            ("escala", StandardScaler())
        ]),
        colunas_numericas
    ),
    (
        "categoricas",
        Pipeline([
            ("nulos", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]),
        colunas_categoricas
    )
])

# ETAPA 6 - DEFINIR OS ALGORITMOS

modelos = {
    "Regressao Logistica": LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=250,
        min_samples_leaf=2,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    )
}

resultados = []

# ETAPA 7 - CRIAR O BASELINE

baseline = DummyClassifier(strategy="most_frequent")

baseline.fit(X_treino, y_treino)

prob_baseline = baseline.predict_proba(X_valid)[:, 1]

ap_baseline = average_precision_score(
    y_valid, prob_baseline
)

resultados.append({
    "modelo": "Baseline",
    "average_precision": ap_baseline
})

# ETAPA 8 - TREINAR E COMPARAR OS MODELOS

melhor_ap = -1
melhor_modelo = None
melhor_nome = None
melhores_probabilidades = None

for nome, algoritmo in modelos.items():

    print("\nTreinando:", nome)

    pipeline = Pipeline([
        ("preprocessamento", preprocessador),
        ("classificador", algoritmo)
    ])

    # Aprender com os dados de treinamento
    pipeline.fit(X_treino, y_treino)

    # Estimar probabilidades na validacao
    probabilidades = pipeline.predict_proba(
        X_valid
    )[:, 1]

    # Calcular Average Precision
    ap = average_precision_score(
        y_valid, probabilidades
    )

    print("Average Precision:", round(ap, 4))

    resultados.append({
        "modelo": nome,
        "average_precision": ap
    })

    if ap > melhor_ap:
        melhor_ap = ap
        melhor_modelo = pipeline
        melhor_nome = nome
        melhores_probabilidades = probabilidades

# ETAPA 9 - SALVAR A COMPARACAO

Path("reports").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)

tabela = pd.DataFrame(resultados)

tabela = tabela.sort_values(
    "average_precision",
    ascending=False
)

print("\nCOMPARACAO DOS MODELOS:")
print(tabela.round(4).to_string(index=False))

tabela.to_csv(
    "reports/comparacao_modelos_validacao.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# ETAPA 10 - SALVAR O MELHOR MODELO

joblib.dump(
    melhor_modelo,
    "models/pipeline_fraudes.joblib"
)

# Guardar as previsoes de validacao
predicoes = pd.DataFrame({
    "transaction_id": df.loc[
        X_valid.index, "transaction_id"
    ].to_numpy(),
    "classe_real": y_valid.to_numpy(),
    "probabilidade_fraude": melhores_probabilidades
})

predicoes.to_csv(
    "reports/predicoes_validacao.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

# Registrar a escolha do modelo
with open(
    "reports/modelo_selecionado.json",
    "w",
    encoding="utf-8"
) as arquivo_json:
    json.dump(
        {
            "modelo": melhor_nome,
            "average_precision_validacao": float(melhor_ap),
            "average_precision_baseline": float(ap_baseline)
        },
        arquivo_json,
        indent=4
    )

print("\nMODELO SELECIONADO:", melhor_nome)
print("Average Precision:", round(melhor_ap, 4))
print("Modelo salvo em models/pipeline_fraudes.joblib")
print("O conjunto de teste ainda nao foi avaliado.")
print("\nTREINAMENTO CONCLUIDO!")
