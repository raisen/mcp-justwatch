FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY src/ src/
RUN pip install --no-cache-dir --no-deps .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "mcp_justwatch.server"]
