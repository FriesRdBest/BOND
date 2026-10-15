FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src

RUN python -m pip install --no-cache-dir -r requirements.txt     && useradd --create-home --uid 10001 bond

COPY app.py ./
COPY .streamlit/config.toml ./.streamlit/config.toml

USER bond

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s     CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8501/_stcore/health', timeout=3)"

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0"]
