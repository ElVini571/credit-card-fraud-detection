# Simulador educativo de fraudes - UFMS
# Use o mesmo Python minor utilizado no treinamento (3.13).
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Estas versões são geradas a partir do ambiente .venv do projeto.
COPY requirements-docker.txt ./requirements-docker.txt
RUN python -m pip install --no-cache-dir -r requirements-docker.txt

# Incluímos somente os arquivos necessários para a execução.
COPY app.py ./app.py
COPY models/pipeline_fraudes.joblib ./models/pipeline_fraudes.joblib
COPY reports/limiar_selecionado.json ./reports/limiar_selecionado.json

# Executar o aplicativo como usuário sem privilégios de administrador.
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

# Verifica se o servidor Streamlit está respondendo.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)" || exit 1

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]
