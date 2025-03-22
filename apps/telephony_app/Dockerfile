FROM vocodedev/vocode:latest

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir --upgrade poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

COPY apps/telephony_app ./apps/telephony_app

CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "3000"]

