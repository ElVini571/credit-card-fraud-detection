r"""Simulador educativo de alerta de fraude - Projeto Integrador UFMS.

Execute na pasta principal do projeto:
    .\.venv\Scripts\python.exe -m streamlit run app.py

O programa usa o modelo e o limiar já selecionados nos scripts anteriores.
Não é um produto para prevenção bancária real.
"""

from pathlib import Path
import json

import joblib
import pandas as pd
import streamlit as st


# O arquivo app.py fica na pasta principal do projeto.
PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_MODELO = PASTA_PROJETO / "models" / "pipeline_fraudes.joblib"
ARQUIVO_LIMIAR = PASTA_PROJETO / "reports" / "limiar_selecionado.json"
ARQUIVO_BASE = PASTA_PROJETO / "data" / "raw" / "Base de Dados - Projeto Integrador (1).xlsx"

st.set_page_config(
    page_title="Simulador de fraudes - UFMS",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Simulador educativo de alertas de fraude")
st.write("Projeto Integrador I | Ciência de Dados — UFMS")
st.warning(
    "Uso exclusivamente educacional. Um alerta não comprova fraude. "
    "Não envie números de cartão, CPF ou outros dados financeiros pessoais reais."
)

# Verificar arquivos gerados nas etapas anteriores.
if not ARQUIVO_MODELO.is_file():
    st.error(f"Modelo não encontrado: {ARQUIVO_MODELO}")
    st.info("Execute primeiro src/02_treinar_modelos.py, na pasta principal do projeto.")
    st.stop()

if not ARQUIVO_LIMIAR.is_file():
    st.error(f"Limiar selecionado não encontrado: {ARQUIVO_LIMIAR}")
    st.info("Execute primeiro src/04_cenarios_limiar.py, na pasta principal do projeto.")
    st.stop()


@st.cache_resource
def carregar_modelo(caminho: str):
    # Carregue apenas o arquivo .joblib produzido por você e em que confia.
    return joblib.load(caminho)


try:
    modelo = carregar_modelo(str(ARQUIVO_MODELO))
    with ARQUIVO_LIMIAR.open("r", encoding="utf-8") as arquivo:
        configuracao = json.load(arquivo)
    limiar_original = float(configuracao["limiar"])
    if not 0 <= limiar_original <= 1:
        raise ValueError("O limiar salvo está fora do intervalo de 0 a 1.")
    # Lista exata de colunas usadas no treinamento, na ordem necessária.
    if hasattr(modelo, "feature_names_in_"):
        colunas_modelo = list(modelo.feature_names_in_)
    else:
        colunas_modelo = list(
            modelo.named_steps["preprocessamento"].feature_names_in_
        )
except Exception as erro:
    st.error("Não foi possível carregar o modelo ou sua configuração.")
    st.code(str(erro))
    st.stop()

st.sidebar.header("Como utilizar")
st.sidebar.write("1. Escolha uma amostra de exemplo ou envie seu CSV.")
st.sidebar.write("2. Ajuste o limiar para simular alertas.")
st.sidebar.write("3. Examine e exporte os resultados.")
st.sidebar.caption("O limiar original veio da validação, não do teste.")

st.subheader("1. Escolha os dados de entrada")
modo = st.radio(
    "Origem das transações",
    ["Usar amostra da planilha do projeto", "Enviar arquivo CSV"],
    horizontal=True,
)

if modo == "Usar amostra da planilha do projeto":
    if not ARQUIVO_BASE.is_file():
        st.error(f"Planilha não encontrada: {ARQUIVO_BASE}")
        st.info("Coloque o Excel em data/raw ou escolha a opção de enviar CSV.")
        st.stop()
    try:
        planilha = pd.read_excel(
            ARQUIVO_BASE,
            sheet_name="credit_card_fraud_2026",
        ).dropna(how="all").dropna(axis=1, how="all")
        dados_entrada = planilha.sample(
            n=min(100, len(planilha)), random_state=42
        ).reset_index(drop=True)
    except Exception as erro:
        st.error("Não foi possível ler a planilha de exemplos.")
        st.code(str(erro))
        st.stop()
    st.caption(
        "Amostra de 100 registros da base original para demonstrar a aplicação. "
        "Esses registros não constituem uma nova avaliação independente do modelo."
    )
    campos_exemplo = ["transaction_id"] + colunas_modelo
    campos_exemplo = [c for c in campos_exemplo if c in dados_entrada.columns]
    csv_exemplo = dados_entrada.loc[:, campos_exemplo].head(20).to_csv(
        index=False, sep=";"
    ).encode("utf-8-sig")
    st.download_button(
        "Baixar CSV de exemplo (20 transações)",
        data=csv_exemplo,
        file_name="exemplo_transacoes_ufms.csv",
        mime="text/csv",
    )
else:
    arquivo_enviado = st.file_uploader(
        "Selecione um CSV com as mesmas colunas de entrada do treinamento",
        type="csv",
    )
    if arquivo_enviado is None:
        st.info("Selecione um arquivo CSV para continuar.")
        st.stop()
    if arquivo_enviado.size > 5 * 1024 * 1024:
        st.error("Para esta demonstração, use um CSV de até 5 MB.")
        st.stop()
    try:
        # Reconhece vírgula ou ponto e vírgula como separador de campos.
        dados_entrada = pd.read_csv(
            arquivo_enviado, sep=None, engine="python", encoding="utf-8-sig"
        )
    except Exception as erro:
        st.error("Não foi possível abrir o arquivo CSV.")
        st.code(str(erro))
        st.stop()

if dados_entrada.empty:
    st.error("O arquivo não possui registros para analisar.")
    st.stop()

if len(dados_entrada) > 5000:
    st.error("Para esta demonstração, envie no máximo 5.000 transações por vez.")
    st.stop()

colunas_faltantes = [c for c in colunas_modelo if c not in dados_entrada.columns]
if colunas_faltantes:
    st.error("O arquivo não contém todas as colunas exigidas pelo modelo.")
    st.write("Colunas ausentes:", colunas_faltantes)
    st.info(
        "Use o botão 'Baixar CSV de exemplo' no modo de amostra para obter "
        "um arquivo com as colunas corretas."
    )
    st.stop()

st.subheader("2. Configure o limiar de alerta")
limiar = st.slider(
    "Alertar quando a pontuação estimada for igual ou maior que:",
    min_value=0.00,
    max_value=1.00,
    value=round(limiar_original, 2),
    step=0.01,
    format="%.2f",
)
st.caption(
    f"Limiar selecionado anteriormente na validação: {limiar_original:.2f}. "
    "Alterar este controle é apenas uma simulação e não muda a avaliação final do teste."
)

# Usamos somente as variáveis que o pipeline conheceu no treinamento.
entradas_modelo = dados_entrada.loc[:, colunas_modelo].copy()
try:
    probabilidades = modelo.predict_proba(entradas_modelo)[:, 1]
except Exception as erro:
    st.error(
        "O modelo não conseguiu processar os dados. Confira os tipos das "
        "colunas (números devem usar o ponto como separador decimal no CSV)."
    )
    st.code(str(erro))
    st.stop()

alertas = (probabilidades >= limiar).astype(int)
resultado = pd.DataFrame(
    {
        "probabilidade_fraude": probabilidades,
        "alerta_modelo": alertas,
    }
)
if "transaction_id" in dados_entrada.columns:
    resultado.insert(0, "transaction_id", dados_entrada["transaction_id"].to_numpy())
if "amount_usd" in dados_entrada.columns:
    resultado.insert(
        1 if "transaction_id" in resultado.columns else 0,
        "amount_usd",
        dados_entrada["amount_usd"].to_numpy(),
    )

st.subheader("3. Resultados da simulação")
a, b, c = st.columns(3)
a.metric("Transações analisadas", f"{len(resultado):,}".replace(",", "."))
b.metric("Alertas produzidos", int(alertas.sum()))
c.metric("Percentual de alertas", f"{alertas.mean():.2%}".replace(".", ","))

st.info(
    "Um alerta significa apenas que a pontuação estimada ultrapassou o "
    "limiar escolhido. Não significa fraude confirmada."
)

# Exibir probabilidades como percentuais para facilitar a leitura.
visualizacao = resultado.copy()
visualizacao["probabilidade_fraude"] = visualizacao[
    "probabilidade_fraude"
].map(lambda p: f"{p:.2%}".replace(".", ","))
st.dataframe(visualizacao, use_container_width=True, hide_index=True)

csv_saida = resultado.to_csv(index=False, sep=";").encode("utf-8-sig")
st.download_button(
    "Baixar resultados em CSV",
    data=csv_saida,
    file_name="alertas_simulados_ufms.csv",
    mime="text/csv",
)

st.caption(
    "Projeto educacional — não conectado a bancos, cartões ou sistemas de pagamento. "
    "Não bloqueia transações nem estima perdas financeiras evitadas."
)
