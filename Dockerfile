# Immagine base Python
FROM python:3.11-slim

# Directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema utili
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e installa le librerie Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta di default per FastAPI
EXPOSE 8000

# Comando di avvio (Uvicorn per eseguire FastAPI)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
