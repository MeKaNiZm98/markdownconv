FROM python:3.9-slim

WORKDIR /app

# Installieren von Abhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Kopieren der Anforderungsdatei und Installation der Abhängigkeiten
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Kopieren des Anwendungscodes
COPY . .

# Streamlit-Konfigurationsverzeichnis erstellen
RUN mkdir -p /root/.streamlit

# Streamlit-Konfiguration erstellen
RUN echo '\
[server]\n\
headless = true\n\
enableCORS = true\n\
enableXsrfProtection = true\n\
port = 8501\n\
address = "0.0.0.0"\n\
baseUrlPath = ""\n\
\n\
[browser]\n\
serverAddress = "localhost"\n\
serverPort = 8501\n\
gatherUsageStats = false\n\
' > /root/.streamlit/config.toml

# Port freigeben
EXPOSE 8501

# Gesundheitscheck hinzufügen
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Anwendung starten
ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]