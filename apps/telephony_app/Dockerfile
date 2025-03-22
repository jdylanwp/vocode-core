FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi

# Fix for libuuid error
RUN apt-get update && apt-get install -y libuuid1

COPY . .

CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "3000"]
