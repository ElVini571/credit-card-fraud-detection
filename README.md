# Detecção de Fraudes em Cartões de Crédito com Machine Learning

**Projeto Integrador I — Ciência de Dados | UFMS Digital**

> Projeto educacional de análise de dados e classificação supervisionada para identificar **transações potencialmente fraudulentas**. Os alertas não comprovam fraude e não são utilizados para bloquear pagamentos reais.

**English summary:** Educational credit-card fraud detection project using Python, scikit-learn, Streamlit, Power BI and Docker. The application estimates a fraud score and simulates alert thresholds; it is not a production banking system.

## Visão geral

Este projeto reúne análise exploratória, treinamento e comparação de classificadores, avaliação separada em treino/validação/teste, dashboard no Power BI e aplicação interativa construída com Streamlit e executável com Docker.

A base estudada tem **20.000 transações**, **26 colunas**, sendo **339 registros rotulados como fraude** (**1,695%**). O conjunto foi dividido com estratificação em 60% treinamento, 20% validação e 20% teste.

## Tecnologias

- **Python:** pandas, NumPy, matplotlib, scikit-learn, joblib
- **Machine Learning:** Regressão Logística, Random Forest e baseline (`DummyClassifier`)
- **Visualização:** Power BI e gráficos Python
- **Aplicação:** Streamlit
- **Ambiente:** Docker e Docker Compose
- **Versionamento:** Git e GitHub

## Resultados documentados

### Comparação na validação

| Modelo | Average Precision (AP) |
| --- | ---: |
| Regressão Logística | **0,2725** |
| Random Forest | 0,1457 |
| Baseline | 0,0170 |

A Regressão Logística foi selecionada pela AP na validação. O limiar de alerta foi escolhido separadamente, maximizando o F1-score nos cenários testados na **validação**. O conjunto de teste não foi utilizado para essa escolha.

### Avaliação final — conjunto de teste (4.000 transações)

| Métrica | Resultado |
| --- | ---: |
| Acurácia | **96,63%** |
| Precisão | **26,24%** |
| Recall | **54,41%** |
| F1-score | **35,41%** |
| Average Precision (AP) | **0,3727** |

**Matriz de confusão:** VN = 3.828; FP = 104; FN = 31; VP = 37. O classificador identificou **37 das 68 fraudes reais** no teste e gerou **104 alertas falsos**. A acurácia, isoladamente, não é uma boa medida nesse conjunto desbalanceado.

> Os números acima correspondem à execução documentada do projeto. Reproduções em outros ambientes devem usar as mesmas versões e o mesmo conjunto de dados para permitir comparação.

## Organização do projeto

```text
.
├── app.py
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── requirements-docker.txt
├── data/raw/                   # base original (licença CC0, conforme fonte)
├── src/                        # auditoria, EDA, treinamento e avaliação
├── models/                     # pipeline salvo (.joblib)
├── reports/                    # métricas, cenários e previsões
│   └── figures/               # gráficos e capturas autorizadas
├── powerbi/                    # dashboard .pbix (quando incluído)
└── docs/                       # metodologia e registros
```

## Executar localmente com Python

Na pasta do projeto, crie um ambiente virtual e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docker.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Acesse `http://localhost:8501`.

## Executar com Docker

É necessário ter Docker Desktop/Engine em execução. A configuração atual é para **uso local**: o `compose.yaml` compartilha a pasta `data/raw/` em modo somente leitura e publica a aplicação apenas no endereço de loopback do computador.

```powershell
docker compose up --build -d
docker compose ps
```

Acesse **http://localhost:8502**. Para encerrar:

```powershell
docker compose down
```

**Atenção:** a imagem Docker não incorpora a planilha `data/raw/`; a montagem local é feita pelo Docker Compose. Para hospedagem pública será preciso adaptar a configuração, definir políticas para arquivos enviados e validar o tratamento dos dados.

## Dashboard Power BI

O relatório tem três páginas: (1) panorama da base completa, (2) desempenho do modelo no teste e (3) simulação de limiares na validação. Esses conjuntos são distintos e não devem ser somados ou confundidos.

## Origem e licença dos dados

Dataset de referência: **Credit Card Fraud Detection 2026**, publicado no Kaggle por **Udit Jain**:

https://www.kaggle.com/datasets/uditjain13/credit-card-fraud-detection-2026

Licença informada na fonte: **CC0 1.0 — Public Domain**: https://creativecommons.org/publicdomain/zero/1.0/

A identificação da origem é mantida como prática acadêmica, embora a CC0 não exija atribuição. A licença dos **dados** não determina automaticamente a licença do **código, imagens, dashboard ou demais contribuições** do projeto.

## Limitações e uso responsável

- Estudo educacional: nenhuma previsão constitui confirmação de fraude.
- A amostra de demonstração do Streamlit não representa uma nova avaliação independente.
- As probabilidades são estimativas do modelo e não devem ser tratadas como chances calibradas sem análise adicional.
- A base é desbalanceada; falsos positivos e falsos negativos têm impactos distintos.
- Recursos/atributos disponíveis apenas após uma transação não devem entrar em um modelo de decisão em tempo real sem auditoria do momento da informação.
- Não envie números reais de cartões, documentos pessoais ou transações privadas à aplicação.
- **Não carregue arquivos `.joblib` não confiáveis**: a desserialização desse formato pode executar código.
- Somar valores rotulados como fraude não comprova dinheiro recuperado ou prejuízo evitado.

## Autoria e contexto acadêmico

Projeto desenvolvido no âmbito do **Projeto Integrador I — UFMS Digital**. Os créditos de equipe e as contribuições individuais devem ser preservados na versão pública; documentação e conteúdo produzidos em grupo não devem ser apresentados como autoria individual exclusiva.

## Próximas melhorias

- Revisar origem temporal e disponibilidade das variáveis usadas pelo modelo.
- Adicionar testes automatizados e pipeline de integração contínua.
- Preparar uma configuração de hospedagem com controles adequados de privacidade e segurança.
- Registrar a apresentação à comunidade e o feedback da ação de extensão.

---

## English — project abstract

A reproducible educational workflow to study **credit-card fraud detection** on an imbalanced dataset. A logistic regression classifier achieved **26.24% precision**, **54.41% recall**, **35.41% F1-score** and **0.3727 Average Precision** on a held-out test set. The repository includes Python scripts, a Power BI report, a Streamlit demo and a local Docker configuration. Predictions are **alerts for review, not confirmed frauds**.
