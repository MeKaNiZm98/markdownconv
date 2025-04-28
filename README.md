# 📄 Dokumenten-Analyzer

Ein benutzerfreundliches Tool zur Dokumentenanalyse, entwickelt mit Streamlit und Microsofts MarkItDown-Technologie. Diese Anwendung ermöglicht es, Inhalte aus verschiedenen Dokumentformaten zu extrahieren und zu analysieren, mit optionaler GPT-4o-Erweiterung für Bildbeschreibungen.

![Document Analyzer Demo](https://github.com/mekanizm98/markdownconv/blob/main/misc/doc-markdown-ms.jpg)

## ✨ Funktionen

- **Unterstützung mehrerer Formate**: Analysiert eine Vielzahl von Dokumentformaten wie PDF, PPTX, DOCX, XLSX, Bilder, Audiodateien und mehr
- **GPT-4o-Integration**: Bildbeschreibungen mit OpenAIs GPT-4o
- **Interaktive Benutzeroberfläche**: Einfache, intuitive Oberfläche, gebaut mit Streamlit
- **Exportfunktion**: Extrahierte Inhalte im Textformat herunterladen
- **Datenschutzfokus**: Temporäre Dateiverarbeitung mit sicherer Löschung
- **Vorschau**: Anzeige der Extraktionsergebnisse im Dokument

## 🎬 Video-Demonstration

Sehen Sie den Dokumenten-Analyzer in Aktion:

<video src="https://github.com/mekanizm98/markdownconv/blob/main/misc/ms_markitdown_git.mp4" controls="controls" style="max-width: 730px;">
</video>

## 🚀 Erste Schritte

### Voraussetzungen

- Python 3.7 oder höher
- OpenAI API-Schlüssel (optional, für GPT-4o-Erweiterung)

### Installation

1. Repository klonen:
    ```bash
    git clone https://github.com/mekanizm98/markdownconv.git
    ```

2. Benötigte Pakete installieren:
    ```bash
    pip install -r requirements.txt
    ```

3. Umgebungsvariablen einrichten (optional):
    ```bash
    # .env-Datei erstellen
    touch .env

    # Deinen OpenAI API-Schlüssel hinzufügen (optional)
    echo "OPENAI_API_KEY=dein_api_schluessel_hier" >> .env
    ```

4. Anwendung starten:
    ```bash
    streamlit run main.py
    ```

## 💻 Nutzung

1. Anwendung starten
2. Dokument über die Seitenleiste hochladen
3. Optional die GPT-4o-Erweiterung aktivieren
4. Extrahierte Inhalte und Dokumentinformationen in den jeweiligen Tabs ansehen
5. Extrahierte Inhalte bei Bedarf herunterladen

## 📋 Unterstützte Formate

- PDF-Dokumente
- PowerPoint-Präsentationen (PPTX)
- Word-Dokumente (DOCX)
- Excel-Tabellen (XLSX)
- Bilder (JPG, PNG) mit EXIF-Daten und OCR
- Audiodateien (MP3, WAV) mit EXIF-Daten und Transkription
- HTML-Dateien
- Textbasierte Dateien (CSV, JSON, XML)

## ⚙️ Konfiguration

Die Anwendung kann über Umgebungsvariablen oder über die Benutzeroberfläche konfiguriert werden:

- `OPENAI_API_KEY`: Dein OpenAI API-Schlüssel für die GPT-4o-Erweiterung
- Individuelle Eingabe des API-Schlüssels in der Benutzeroberfläche verfügbar
- Cache-Verwaltung mit integrierter Löschfunktion

## 📝 Lizenz & MS-Repository

Dieses Projekt steht unter der MIT-Lizenz – Details siehe [LICENSE](LICENSE).

Original MS MarkItDown-Repository: [https://github.com/microsoft/markitdown](https://github.com/microsoft/markitdown)

## 🙏 Danksagungen

- Microsoft MarkItDown-Technologie
- Streamlit-Framework
- OpenAI GPT-4o (optionale Integration)
- lesteroliver911/microsoft-markitdown-streamlit-ui
