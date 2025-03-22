FROM vocodedev/vocode:latest

WORKDIR /app

# Add missing system dependencies
RUN apt-get update && apt-get install -y libuuid1 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction

COPY . .

CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "3000"]
