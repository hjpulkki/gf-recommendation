FROM python:3.13-slim

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean

# Install Poetry
ENV POETRY_VERSION=2.0.1
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH="/root/.local/bin:$PATH"

# Copy project files and install poetry environment
WORKDIR /app
COPY . /app/
RUN poetry install --no-root

# Run app
WORKDIR /app/src
CMD ["poetry", "run", "python", "app.py"]
