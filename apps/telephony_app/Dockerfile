# Use the official Vocode base image or Python if needed
FROM vocodedev/vocode:latest

# Set the working directory inside the container
WORKDIR /app

# Copy Poetry setup files to install dependencies
COPY pyproject.toml poetry.lock ./

# Install Poetry and dependencies
RUN pip install --upgrade pip poetry \
 && poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction

# Copy all code into the container
COPY . .

# Set the default command to run your app
CMD ["uvicorn", "apps.telephony_app.main:app", "--host", "0.0.0.0", "--port", "3000"]
