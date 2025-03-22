FROM python:3.10-slim

RUN apt-get update && apt-get install -y ffmpeg git

WORKDIR /app

COPY . .

RUN pip install poetry && poetry install --no-dev --no-interaction

EXPOSE 3000

CMD ["poetry", "run", "uvicorn", "telephony_app.main:app", "--host", "0.0.0.0", "--port", "3000"]
