FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    psycopg2-binary \
    python-dotenv \
    python-telegram-bot \
    openpyxl \
    requests

CMD ["python3", "bot.py"]