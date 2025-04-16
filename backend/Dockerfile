FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Zkopíruj potřebné soubory a adresáře se zachováním původní struktury
COPY src/app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY entrypoint.sh ./

# Udělej entrypoint skript spustitelným
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Nastav entrypoint skript (Dočasně zakomentováno)
# ENTRYPOINT ["/app/entrypoint.sh"]

# Původní příkaz, který se předá entrypoint skriptu
# Uvicorn nyní najde app.main v /app/app/main.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
