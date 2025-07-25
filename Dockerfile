FROM python:3.10-slim

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY requirements.runpod.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# TODO: delete this
RUN pip install ruff && ruff check scripts/
ENV PYTHONPATH=/app

CMD ["python", "-u", "scripts/runpod_handler.py"]
