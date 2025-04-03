FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Kopíruj celý obsah aktuálního adresáře (backend) do /app
COPY . .

# Udělej entrypoint skript spustitelným
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Nastav entrypoint skript
ENTRYPOINT ["/app/entrypoint.sh"]

# Původní příkaz, který se předá entrypoint skriptu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
