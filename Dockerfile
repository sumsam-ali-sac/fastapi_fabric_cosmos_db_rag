FROM python:3.11-slim

WORKDIR /app
RUN pip install --no-cache-dir pdm

COPY pyproject.toml pdm.lock /app/

RUN pdm install --prod

COPY . /app

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["pdm", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
