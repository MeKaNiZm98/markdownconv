"""
Document Analyzer with Microsoft MarkItDown and LLM-based Image Description

This Streamlit application allows users to upload documents (including PDFs) and have their 
contents extracted, analyzed, and optionally enhanced by a Large Language Model (LLM). 
If enabled, embedded images in PDF pages can be individually extracted and described by 
the LLM, integrating figure references seamlessly into the extracted text.

Installation and Requirements:
1. Python 3.8 or newer is recommended.
2. Install Streamlit:
   ```bash
   pip install streamlit
"""

import streamlit as st
import os
from markitdown import MarkItDown
from pathlib import Path
import tempfile
from dotenv import load_dotenv
import requests
from types import SimpleNamespace
import pdfplumber
from PIL import Image
import base64

# Attempt to import OpenAI; if not available, set OpenAI = None
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Load environment variables
load_dotenv()

debug_logs = []
def log_debug(message: str):
    debug_logs.append(message)

# Translation dictionaries
translations = {
    "en": {
        "page_title": "Document Analyzer with Microsoft MarkItDown",
        "app_title": "📄 Document Analyzer with Microsoft MarkItDown",
        "app_description": "Upload a PDF or other document to extract text and analyze embedded images using LLM.",
        "file_uploader": "Choose a file",
        "settings_header": "Settings",
        "use_llm_toggle": "Use LLM for Enhanced Analysis",
        "llm_provider_header": "LLM Provider",
        "select_llm_provider": "Select LLM Provider",
        "openai_api_key": "OpenAI API Key",
        "api_key_help": "Your API key will not be stored and is only used for this session",
        "local_llm_url": "Local LLM URL",
        "local_llm_help": "URL for your local LLM server",
        "clear_cache": "Clear Cache",
        "cache_cleared": "Cache cleared!",
        "supported_formats": "Supported Formats:",
        "processing": "Processing document...",
        "analysis_results": "Analysis Results",
        "tab_extracted": "Extracted Content",
        "tab_info": "Document Information",
        "tab_debug": "Debug Logs",
        "download_button": "Download Extracted Content",
        "debug_logs_title": "Debug Logs:",
        "no_debug_logs": "No debug logs available.",
        "error_processing": "Error processing document:",
        "upload_prompt": "👈 Please upload a document using the sidebar to begin analysis",
        "language_selector": "Language / Sprache",
        "figure_text": "Figure",
        "document_language": "Document Language",
        "document_language_help": "Select the main language of the document. The LLM will be informed that other languages may also be present.",
        "auto_detect": "Auto-detect",
        "multilingual_prompt": "This document is primarily in {}, but may contain content in other languages as well.",
        "drag_drop_text": "Drag and drop files here or browse files"
    },
    "de": {
        "page_title": "Dokumentenanalyse mit Microsoft MarkItDown",
        "app_title": "📄 Dokumentenanalyse mit Microsoft MarkItDown",
        "app_description": "Laden Sie ein PDF oder anderes Dokument hoch, um Text zu extrahieren und eingebettete Bilder mit LLM zu analysieren.",
        "file_uploader": "Datei auswählen",
        "settings_header": "Einstellungen",
        "use_llm_toggle": "LLM für erweiterte Analyse verwenden",
        "llm_provider_header": "LLM-Anbieter",
        "select_llm_provider": "LLM-Anbieter auswählen",
        "openai_api_key": "OpenAI API-Schlüssel",
        "api_key_help": "Ihr API-Schlüssel wird nicht gespeichert und nur für diese Sitzung verwendet",
        "local_llm_url": "Lokale LLM-URL",
        "local_llm_help": "URL für Ihren lokalen LLM-Server",
        "clear_cache": "Cache leeren",
        "cache_cleared": "Cache geleert!",
        "supported_formats": "Unterstützte Formate:",
        "processing": "Dokument wird verarbeitet...",
        "analysis_results": "Analyseergebnisse",
        "tab_extracted": "Extrahierter Inhalt",
        "tab_info": "Dokumentinformationen",
        "tab_debug": "Debug-Protokolle",
        "download_button": "Extrahierten Inhalt herunterladen",
        "debug_logs_title": "Debug-Protokolle:",
        "no_debug_logs": "Keine Debug-Protokolle verfügbar.",
        "error_processing": "Fehler bei der Verarbeitung des Dokuments:",
        "upload_prompt": "👈 Bitte laden Sie ein Dokument über die Seitenleiste hoch, um mit der Analyse zu beginnen",
        "language_selector": "Sprache / Language",
        "figure_text": "Abbildung",
        "drag_drop_text": "Dateien hierher ziehen und ablegen oder durchsuchen",
        "extract_images_text": "Extrahiert Text und Bilder und beschreibt Bilder inline, wenn LLM aktiviert ist",
        "document_language": "Dokumentsprache",
        "document_language_help": "Wählen Sie die Hauptsprache des Dokuments. Das LLM wird darüber informiert, dass auch andere Sprachen vorhanden sein können.",
        "auto_detect": "Automatisch erkennen",
        "multilingual_prompt": "Dieses Dokument ist hauptsächlich in {} verfasst, kann aber auch Inhalte in anderen Sprachen enthalten."
    },
    "fr": {
        "page_title": "Analyseur de Documents avec Microsoft MarkItDown",
        "app_title": "📄 Analyseur de Documents avec Microsoft MarkItDown",
        "app_description": "Téléchargez un PDF ou un autre document pour extraire du texte et analyser les images intégrées à l'aide de LLM.",
        "file_uploader": "Choisir un fichier",
        "settings_header": "Paramètres",
        "use_llm_toggle": "Utiliser LLM pour une analyse améliorée",
        "llm_provider_header": "Fournisseur LLM",
        "select_llm_provider": "Sélectionner le fournisseur LLM",
        "openai_api_key": "Clé API OpenAI",
        "api_key_help": "Votre clé API ne sera pas stockée et n'est utilisée que pour cette session",
        "local_llm_url": "URL LLM locale",
        "local_llm_help": "URL pour votre serveur LLM local",
        "clear_cache": "Vider le cache",
        "cache_cleared": "Cache vidé !",
        "supported_formats": "Formats pris en charge :",
        "processing": "Traitement du document...",
        "analysis_results": "Résultats d'analyse",
        "tab_extracted": "Contenu extrait",
        "tab_info": "Informations sur le document",
        "tab_debug": "Journaux de débogage",
        "download_button": "Télécharger le contenu extrait",
        "debug_logs_title": "Journaux de débogage :",
        "no_debug_logs": "Aucun journal de débogage disponible.",
        "error_processing": "Erreur lors du traitement du document :",
        "upload_prompt": "👈 Veuillez télécharger un document à l'aide de la barre latérale pour commencer l'analyse",
        "language_selector": "Langue / Sprache",
        "figure_text": "Figure",
        "drag_drop_text": "Glissez-déposez des fichiers ici ou parcourez les fichiers",
        "extract_images_text": "Extrai le texte et les images et décrit les images en ligne si LLM est activé",
        "document_language": "Langue du document",
        "document_language_help": "Sélectionnez la langue principale du document. Le LLM sera informé que d'autres langues peuvent également être présentes.",
        "auto_detect": "Détection automatique",
        "multilingual_prompt": "Ce document est principalement en {}, mais peut également contenir du contenu dans d'autres langues."
    },
    "es": {
        "page_title": "Analizador de Documentos con Microsoft MarkItDown",
        "app_title": "📄 Analizador de Documentos con Microsoft MarkItDown",
        "app_description": "Suba un PDF u otro documento para extraer texto y analizar imágenes incrustadas usando LLM.",
        "file_uploader": "Elegir un archivo",
        "settings_header": "Configuración",
        "use_llm_toggle": "Usar LLM para análisis mejorado",
        "llm_provider_header": "Proveedor de LLM",
        "select_llm_provider": "Seleccionar proveedor de LLM",
        "openai_api_key": "Clave API de OpenAI",
        "api_key_help": "Su clave API no se almacenará y solo se usa para esta sesión",
        "local_llm_url": "URL de LLM local",
        "local_llm_help": "URL para su servidor LLM local",
        "clear_cache": "Limpiar caché",
        "cache_cleared": "¡Caché limpiada!",
        "supported_formats": "Formatos soportados:",
        "processing": "Procesando documento...",
        "analysis_results": "Resultados del análisis",
        "tab_extracted": "Contenido extraído",
        "tab_info": "Información del documento",
        "tab_debug": "Registros de depuración",
        "download_button": "Descargar contenido extraído",
        "debug_logs_title": "Registros de depuración:",
        "no_debug_logs": "No hay registros de depuración disponibles.",
        "error_processing": "Error al procesar el documento:",
        "upload_prompt": "👈 Por favor, suba un documento usando la barra lateral para comenzar el análisis",
        "language_selector": "Idioma / Sprache",
        "figure_text": "Figura",
        "drag_drop_text": "Arrastre y solte archivos aquí o explore archivos",
        "extract_images_text": "Extrae texto e imágenes y describe imágenes en línea si LLM está habilitado",
        "document_language": "Idioma del documento",
        "document_language_help": "Selecione el idioma principal del documento. Se informará al LLM que también pueden estar presentes otros idiomas.",
        "auto_detect": "Detección automática",
        "multilingual_prompt": "Este documento está principalmente en {}, pero también puede contener contenido en otros idiomas."
    },
    "it": {
        "page_title": "Analizzatore di Documenti con Microsoft MarkItDown",
        "app_title": "📄 Analizzatore di Documenti con Microsoft MarkItDown",
        "app_description": "Carica un PDF o un altro documento per estrarre testo e analizzare immagini incorporate utilizzando LLM.",
        "file_uploader": "Scegli un file",
        "settings_header": "Impostazioni",
        "use_llm_toggle": "Usa LLM per analisi avanzata",
        "llm_provider_header": "Provider LLM",
        "select_llm_provider": "Seleziona provider LLM",
        "openai_api_key": "Chiave API OpenAI",
        "api_key_help": "La tua chiave API non verrà memorizzata e viene utilizzata solo per questa sessione",
        "local_llm_url": "URL LLM locale",
        "local_llm_help": "URL per il tuo server LLM locale",
        "clear_cache": "Cancella cache",
        "cache_cleared": "Cache cancellata!",
        "supported_formats": "Formati supportati:",
        "processing": "Elaborazione documento...",
        "analysis_results": "Risultati dell'analisi",
        "tab_extracted": "Contenuto estratto",
        "tab_info": "Informazioni documento",
        "tab_debug": "Log di debug",
        "download_button": "Scarica contenuto estratto",
        "debug_logs_title": "Log di debug:",
        "no_debug_logs": "Nessun log di debug disponibile.",
        "error_processing": "Errore durante l'elaborazione del documento:",
        "upload_prompt": "👈 Carica un documento utilizzando la barra laterale per iniziare l'analisi",
        "language_selector": "Lingua / Sprache",
        "figure_text": "Figura",
        "drag_drop_text": "Trascina e rilascia i file qui o sfoglia i file",
        "extract_images_text": "Estrae testo e immagini e descrive le immagini in linea se LLM è abilitato",
        "document_language": "Lingua del documento",
        "document_language_help": "Seleziona la lingua principale del documento. Il LLM sarà informato che potrebbero essere presenti anche altre lingue.",
        "auto_detect": "Rilevamento automatico",
        "multilingual_prompt": "Questo documento è principalmente in {}, ma può contenere anche contenuti in altre lingue."
    },
    "nl": {
        "page_title": "Documentanalyse met Microsoft MarkItDown",
        "app_title": "📄 Documentanalyse met Microsoft MarkItDown",
        "app_description": "Upload een PDF of ander document om tekst te extraheren en ingesloten afbeeldingen te analyseren met behulp van LLM.",
        "file_uploader": "Kies een bestand",
        "settings_header": "Instellingen",
        "use_llm_toggle": "Gebruik LLM voor verbeterde analyse",
        "llm_provider_header": "LLM-provider",
        "select_llm_provider": "Selecteer LLM-provider",
        "openai_api_key": "OpenAI API-sleutel",
        "api_key_help": "Uw API-sleutel wordt niet opgeslagen en wordt alleen gebruikt voor deze sessie",
        "local_llm_url": "Lokale LLM-URL",
        "local_llm_help": "URL voor uw lokale LLM-server",
        "clear_cache": "Cache wissen",
        "cache_cleared": "Cache gewist!",
        "supported_formats": "Ondersteunde formaten:",
        "processing": "Document verwerken...",
        "analysis_results": "Analyseresultaten",
        "tab_extracted": "Geëxtraheerde inhoud",
        "tab_info": "Documentinformatie",
        "tab_debug": "Debug-logboeken",
        "download_button": "Download geëxtraheerde inhoud",
        "debug_logs_title": "Debug-logboeken:",
        "no_debug_logs": "Geen debug-logboeken beschikbaar.",
        "error_processing": "Fout bij het verwerken van document:",
        "upload_prompt": "👈 Upload een document via de zijbalk om de analyse te starten",
        "language_selector": "Taal / Sprache",
        "figure_text": "Figuur",
        "drag_drop_text": "Sleep bestanden hierheen of blader door bestanden",
        "extract_images_text": "Extraheert tekst en afbeeldingen en beschrijft afbeeldingen inline als LLM is ingeschakeld",
        "document_language": "Documenttaal",
        "document_language_help": "Selecteer de hoofdtaal van het document. De LLM wordt geïnformeerd dat er ook andere talen aanwezig kunnen zijn.",
        "auto_detect": "Automatisch detecteren",
        "multilingual_prompt": "Dit document is voornamelijk in {}, maar kan ook inhoud in andere talen bevatten."
    },
    "pt": {
        "page_title": "Analisador de Documentos com Microsoft MarkItDown",
        "app_title": "📄 Analisador de Documentos com Microsoft MarkItDown",
        "app_description": "Carregue um PDF ou outro documento para extrair texto e analisar imagens incorporadas usando LLM.",
        "file_uploader": "Escolher um arquivo",
        "settings_header": "Configurações",
        "use_llm_toggle": "Usar LLM para análise aprimorada",
        "llm_provider_header": "Provedor de LLM",
        "select_llm_provider": "Selecionar provedor de LLM",
        "openai_api_key": "Chave API OpenAI",
        "api_key_help": "Sua chave API não será armazenada e é usada apenas para esta sessão",
        "local_llm_url": "URL LLM local",
        "local_llm_help": "URL para seu servidor LLM local",
        "clear_cache": "Limpar cache",
        "cache_cleared": "Cache limpo!",
        "supported_formats": "Formatos suportados:",
        "processing": "Processando documento...",
        "analysis_results": "Resultados da análise",
        "tab_extracted": "Conteúdo extraído",
        "tab_info": "Informações do documento",
        "tab_debug": "Registros de depuração",
        "download_button": "Baixar conteúdo extraído",
        "debug_logs_title": "Registros de depuração:",
        "no_debug_logs": "Nenhum registro de depuração disponível.",
        "error_processing": "Erro ao processar o documento:",
        "upload_prompt": "👈 Por favor, carregue um documento usando a barra lateral para iniciar a análise",
        "language_selector": "Idioma / Sprache",
        "figure_text": "Figura",
        "drag_drop_text": "Arraste e solte arquivos aqui ou navegue pelos arquivos",
        "extract_images_text": "Extrai texto e imagens e descreve imagens em linha se o LLM estiver ativado",
        "document_language": "Idioma do documento",
        "document_language_help": "Selecione o idioma principal do documento. O LLM será informado que outros idiomas também podem estar presentes.",
        "auto_detect": "Detecção automática",
        "multilingual_prompt": "Este documento é principalmente em {}, mas também pode conter conteúdo em outros idiomas."
    },
    "ru": {
        "page_title": "Анализатор документов с Microsoft MarkItDown",
        "app_title": "📄 Анализатор документов с Microsoft MarkItDown",
        "app_description": "Загрузите PDF или другой документ для извлечения текста и анализа встроенных изображений с помощью LLM.",
        "file_uploader": "Выбрать файл",
        "settings_header": "Настройки",
        "use_llm_toggle": "Использовать LLM для расширенного анализа",
        "llm_provider_header": "Поставщик LLM",
        "select_llm_provider": "Выбрать поставщика LLM",
        "openai_api_key": "Ключ API OpenAI",
        "api_key_help": "Ваш ключ API не будет сохранен и используется только для этой сессии",
        "local_llm_url": "Локальный URL LLM",
        "local_llm_help": "URL для вашего локального сервера LLM",
        "clear_cache": "Очистить кэш",
        "cache_cleared": "Кэш очищен!",
        "supported_formats": "Поддерживаемые форматы:",
        "processing": "Обработка документа...",
        "analysis_results": "Результаты анализа",
        "tab_extracted": "Извлеченный контент",
        "tab_info": "Информация о документе",
        "tab_debug": "Журналы отладки",
        "download_button": "Скачать извлеченный контент",
        "debug_logs_title": "Журналы отладки:",
        "no_debug_logs": "Журналы отладки недоступны.",
        "error_processing": "Ошибка при обработке документа:",
        "upload_prompt": "👈 Пожалуйста, загрузите документ с помощью боковой панели, чтобы начать анализ",
        "language_selector": "Язык / Sprache",
        "figure_text": "Рисунок",
        "drag_drop_text": "Перетащите файлы сюда или просмотрите файлы",
        "extract_images_text": "Извлекает текст и изображения и описывает изображения в тексте, если включен LLM",
        "document_language": "Язык документа",
        "document_language_help": "Выберите основной язык документа. LLM будет проинформирован о том, что могут присутствовать и другие языки.",
        "auto_detect": "Автоопределение",
        "multilingual_prompt": "Этот документ в основном на {}, но также может содержать контент на других языках."
    },
    "zh": {
        "page_title": "Microsoft MarkItDown 文档分析器",
        "app_title": "📄 Microsoft MarkItDown 文档分析器",
        "app_description": "上传 PDF 或其他文档以提取文本并使用 LLM 分析嵌入的图像。",
        "file_uploader": "选择文件",
        "settings_header": "设置",
        "use_llm_toggle": "使用 LLM 进行增强分析",
        "llm_provider_header": "LLM 提供商",
        "select_llm_provider": "选择 LLM 提供商",
        "openai_api_key": "OpenAI API 密钥",
        "api_key_help": "您的 API 密钥不会被存储，仅用于此会话",
        "local_llm_url": "本地 LLM URL",
        "local_llm_help": "您的本地 LLM 服务器的 URL",
        "clear_cache": "清除缓存",
        "cache_cleared": "缓存已清除！",
        "supported_formats": "支持的格式：",
        "processing": "正在处理文档...",
        "analysis_results": "分析结果",
        "tab_extracted": "提取的内容",
        "tab_info": "文档信息",
        "tab_debug": "调试日志",
        "download_button": "下载提取的内容",
        "debug_logs_title": "调试日志：",
        "no_debug_logs": "没有可用的调试日志。",
        "error_processing": "处理文档时出错：",
        "upload_prompt": "👈 请使用侧边栏上传文档以开始分析",
        "language_selector": "语言 / Sprache",
        "figure_text": "图",
        "drag_drop_text": "将文件拖放到此处或浏览文件",
        "extract_images_text": "提取文本和图像，如果启用了 LLM，则内联描述图像",
        "document_language": "文档语言",
        "document_language_help": "选择文档的主要语言。LLM 将被告知可能还存在其他语言。",
        "auto_detect": "自动检测",
        "multilingual_prompt": "此文档主要使用 {}，但也可能包含其他语言的内容。"
    },
    "ja": {
        "page_title": "Microsoft MarkItDown ドキュメント分析ツール",
        "app_title": "📄 Microsoft MarkItDown ドキュメント分析ツール",
        "app_description": "PDFやその他のドキュメントをアップロードして、テキストを抽出し、LLMを使用して埋め込み画像を分析します。",
        "file_uploader": "ファイルを選択",
        "settings_header": "設定",
        "use_llm_toggle": "拡張分析にLLMを使用",
        "llm_provider_header": "LLMプロバイダー",
        "select_llm_provider": "LLMプロバイダーを選択",
        "openai_api_key": "OpenAI APIキー",
        "api_key_help": "APIキーは保存されず、このセッションでのみ使用されます",
        "local_llm_url": "ローカルLLM URL",
        "local_llm_help": "ローカルLLMサーバーのURL",
        "clear_cache": "キャッシュをクリア",
        "cache_cleared": "キャッシュがクリアされました！",
        "supported_formats": "サポートされている形式：",
        "processing": "ドキュメントを処理中...",
        "analysis_results": "分析結果",
        "tab_extracted": "抽出されたコンテンツ",
        "tab_info": "ドキュメント情報",
        "tab_debug": "デバッグログ",
        "download_button": "抽出されたコンテンツをダウンロード",
        "debug_logs_title": "デバッグログ：",
        "no_debug_logs": "利用可能なデバッグログはありません。",
        "error_processing": "ドキュメントの処理中にエラーが発生しました：",
        "upload_prompt": "👈 サイドバーを使用してドキュメントをアップロードし、分析を開始してください",
        "language_selector": "言語 / Sprache",
        "figure_text": "図",
        "drag_drop_text": "ファイルをここにドラッグ＆ドロップするか、ファイルを参照",
        "extract_images_text": "テキストと画像を抽出し、LLMが有効な場合は画像をインラインで説明します",
        "document_language": "ドキュメント言語",
        "document_language_help": "ドキュメントの主要言語を選択してください。LLMには他の言語も存在する可能性があることが通知されます。",
        "auto_detect": "自動検出",
        "multilingual_prompt": "このドキュメントは主に{}で書かれていますが、他の言語のコンテンツも含まれている可能性があります。"
    }
}

class LocalLLMClient:
    def __init__(self, base_url="http://127.0.0.1:1234/v1/chat/completions"):
        self.base_url = base_url
        self.chat = self.Chat(self.base_url)

    class Chat:
        def __init__(self, base_url):
            self.base_url = base_url
            self.completions = LocalLLMClient.Chat.Completions(self.base_url)

        class Completions:
            def __init__(self, base_url):
                self.base_url = base_url

            def create(self, model, messages, temperature=0.7, max_tokens=-1, stream=False):
                log_debug("Preparing to send request to local LLM...")
                payload_size = 0
                for m in messages:
                    if isinstance(m.get("content"), list):
                        for c in m["content"]:
                            if c.get("type") == "image_url" and "data:image" in c["image_url"]["url"]:
                                image_data = c["image_url"]["url"].split(",")[1]
                                payload_size = len(image_data)
                                if payload_size > 3_000_000:
                                    log_debug("Image is too large to process with LLM.")
                                    return self._convert_to_objects({
                                        "choices": [{
                                            "message": {
                                                "role": "assistant",
                                                "content": "Image too large to process."
                                            }
                                        }]
                                    })

                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": stream
                }
                log_debug(f"Request Payload: {payload}")
                try:
                    response = requests.post(self.base_url, json=payload, timeout=60)
                    log_debug(f"Request sent to {self.base_url}. HTTP status: {response.status_code}")
                    if response.status_code != 200:
                        log_debug(f"Non-200 status code: {response.status_code}")
                    data = response.json()
                    log_debug(f"Response JSON from LLM: {data}")
                    return self._convert_to_objects(data)
                except requests.Timeout:
                    log_debug("LLM request timed out.")
                    return self._convert_to_objects({
                        "choices": [{
                            "message": {
                                "role": "assistant",
                                "content": "The LLM request timed out."
                            }
                        }]
                    })
                except Exception as e:
                    log_debug(f"Error making LLM request: {str(e)}")
                    raise e

            def _convert_to_objects(self, data):
                def dict_to_namespace(d):
                    if isinstance(d, dict):
                        for k, v in d.items():
                            d[k] = dict_to_namespace(v)
                        return SimpleNamespace(**d)
                    elif isinstance(d, list):
                        return [dict_to_namespace(x) for x in d]
                    else:
                        return d
                return dict_to_namespace(data)

def clear_cache():
    if os.path.exists(".cache"):
        for file in os.listdir(".cache"):
            os.remove(os.path.join(".cache", file))
    st.cache_data.clear()
    log_debug("Cache cleared.")

def image_to_data_uri(pil_img):
    buffered = tempfile.TemporaryFile()
    pil_img.save(buffered, format="PNG")
    buffered.seek(0)
    img_str = base64.b64encode(buffered.read()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"

def describe_image_with_llm(llm_client, llm_model, pil_img, doc_lang="auto", ui_lang="en"):
    with tempfile.TemporaryFile() as buffered:
        pil_img.save(buffered, format="PNG")
        buffered.seek(0)
        img_str = base64.b64encode(buffered.read()).decode("utf-8")
    
    data_uri = f"data:image/png;base64,{img_str}"
    
    # Sprachhinweis für das LLM hinzufügen
    prompt_text = "Describe this image in detail:"
    
    if doc_lang != "auto":
        # Bei doc_lang="auto" verwenden wir Englisch als UI-Sprache
        t = translations["en"] if doc_lang == "auto" else translations[ui_lang]
        language_name = {"de": "German", "en": "English", "fr": "French", "es": "Spanish", 
                         "it": "Italian", "nl": "Dutch", "pt": "Portuguese", 
                         "ru": "Russian", "zh": "Chinese", "ja": "Japanese"}.get(doc_lang, doc_lang)
        
        if doc_lang != "auto":
            multilingual_hint = t["multilingual_prompt"].format(language_name)
            prompt_text = f"{prompt_text}\n{multilingual_hint}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": data_uri}
                }
            ]
        }
    ]
    response = llm_client.chat.completions.create(model=llm_model, messages=messages)
    return response.choices[0].message.content.strip()

def process_pdf_with_images_and_text(md, tmp_path, llm_client, llm_model, ui_lang="de", doc_lang="auto"):
    log_debug("Extracting text and images from PDF using pdfplumber.")
    text_pages = []
    figure_counter = 1
    figure_text = translations[ui_lang]["figure_text"]

    with pdfplumber.open(tmp_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract text
            text = page.extract_text() or ""
            lines = text.split('\n')
            words = page.extract_words()

            # Approximate line positions
            line_positions = []
            for ln in lines:
                ln_words = [w for w in words if w['text'] in ln]
                if ln_words:
                    avg_y = sum(w['top'] for w in ln_words) / len(ln_words)
                else:
                    avg_y = None
                line_positions.append((ln, avg_y))

            # Extract images from the page
            # page.images returns a list of image dictionaries with keys: x0, y0, x1, y1
            figs = []
            page_img = page.to_image(resolution=150)
            pil_page_img = page_img.original  # Get the underlying PIL image

            for im in page.images:
                x0, y0, x1, y1 = im['x0'], im['y0'], im['x1'], im['y1']
                # Crop the PIL image at the bounding box of the image
                cropped = pil_page_img.crop((x0, y0, x1, y1))
                
                # Describe the image with LLM
                # Dokumentsprache an LLM weitergeben
                fig_desc = describe_image_with_llm(llm_client, llm_model, cropped, doc_lang, ui_lang)
                fig_y_mid = y0 + (y1 - y0) / 2.0
                figs.append((fig_y_mid, f"{figure_text} {figure_counter}: {fig_desc}"))
                figure_counter += 1
            
            figs.sort(key=lambda f: f[0])

            # Integrate figures into text output
            output_lines = []
            fig_idx = 0
            for (ln, avg_y) in line_positions:
                output_lines.append(ln)
                while fig_idx < len(figs):
                    fig_y, fig_text = figs[fig_idx]
                    if avg_y is not None and fig_y >= avg_y:
                        output_lines.append(fig_text)
                        fig_idx += 1
                    else:
                        break

            # If any figures remain unmatched, place them at the end
            while fig_idx < len(figs):
                output_lines.append(figs[fig_idx][1])
                fig_idx += 1

            page_output = "\n".join(output_lines)
            text_pages.append(f"--- Page {page_num} ---\n{page_output}")

    return "\n\n".join(text_pages)

def process_document(uploaded_file, use_llm=False, llm_provider="Local", custom_api_key=None, local_llm_url=None, ui_lang="de", doc_lang="auto"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        if use_llm:
            if llm_provider == "OpenAI":
                if OpenAI is None:
                    raise RuntimeError("OpenAI library not installed.")
                api_key = custom_api_key or os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OpenAI API key is required.")
                log_debug("Using OpenAI API client.")
                client = OpenAI(api_key=api_key)
                md = MarkItDown(llm_client=client, llm_model="gpt-4o")
                llm_client = client
                llm_model = "gpt-4o"
            else:
                log_debug("Using Local LLM client.")
                llm_client = LocalLLMClient(base_url=local_llm_url or "http://127.0.0.1:1234/v1/chat/completions")
                llm_model = "llama-3.1-unhinged-vision-8b"
                md = MarkItDown(llm_client=llm_client, llm_model=llm_model)
        else:
            log_debug("Not using LLM.")
            md = MarkItDown()
            llm_client = None
            llm_model = None

        extension = Path(uploaded_file.name).suffix.lower()
        # If PDF and LLM is enabled, do the image+text extraction via pdfplumber
        if extension == ".pdf" and use_llm:
            text_content = process_pdf_with_images_and_text(md, tmp_path, llm_client, llm_model, ui_lang, doc_lang)
        else:
            # Otherwise, just convert normally
            log_debug(f"Converting file with MarkItDown: {tmp_path}")
            result = md.convert(tmp_path)
            text_content = result.text_content.strip() if result and result.text_content else ""

        return text_content
    except Exception as e:
        log_debug(f"Error during document processing: {str(e)}")
        raise e
    finally:
        os.unlink(tmp_path)
        log_debug(f"Temporary file {tmp_path} removed.")

def main():
    # Initialize session state for language selection
    if 'language' not in st.session_state:
        st.session_state.language = "de"  # Default to German
    
    # Get current language
    lang = st.session_state.language
    t = translations[lang]
    
    st.set_page_config(
        page_title=t["page_title"],
        page_icon="📄",
        layout="wide"
    )
    
    with st.sidebar:
        # Sprachauswahl ganz oben in der Seitenleiste platzieren
        lang_option = st.selectbox(
            t["language_selector"],
            options=["🇩🇪 Deutsch", "🇬🇧 English", "🇫🇷 Français", "🇪🇸 Español", "🇮🇹 Italiano", 
                    "🇳🇱 Nederlands", "🇵🇹 Português", "🇷🇺 Русский", "🇨🇳 中文", "🇯🇵 日本語"],
            index=0 if lang == "de" else 1 if lang == "en" else 2 if lang == "fr" else 
                  3 if lang == "es" else 4 if lang == "it" else 5 if lang == "nl" else
                  6 if lang == "pt" else 7 if lang == "ru" else 8 if lang == "zh" else 9
        )
        
        # Sprache basierend auf Auswahl aktualisieren
        if lang_option == "🇬🇧 English" and lang != "en":
            st.session_state.language = "en"
            st.experimental_rerun()
        elif lang_option == "🇩🇪 Deutsch" and lang != "de":
            st.session_state.language = "de"
            st.experimental_rerun()
        elif lang_option == "🇫🇷 Français" and lang != "fr":
            st.session_state.language = "fr"
            st.experimental_rerun()
        elif lang_option == "🇪🇸 Español" and lang != "es":
            st.session_state.language = "es"
            st.experimental_rerun()
        elif lang_option == "🇮🇹 Italiano" and lang != "it":
            st.session_state.language = "it"
            st.experimental_rerun()
        elif lang_option == "🇳🇱 Nederlands" and lang != "nl":
            st.session_state.language = "nl"
            st.experimental_rerun()
        elif lang_option == "🇵🇹 Português" and lang != "pt":
            st.session_state.language = "pt"
            st.experimental_rerun()
        elif lang_option == "🇷🇺 Русский" and lang != "ru":
            st.session_state.language = "ru"
            st.experimental_rerun()
        elif lang_option == "🇨🇳 中文" and lang != "zh":
            st.session_state.language = "zh"
            st.experimental_rerun()
        elif lang_option == "🇯🇵 日本語" and lang != "ja":
            st.session_state.language = "ja"
            st.experimental_rerun()
            
        # Titel und Beschreibung nach der Sprachauswahl
        st.title(t["app_title"])
        st.write(t["app_description"])
        
        uploaded_file = st.file_uploader(
            t["file_uploader"], 
            type=['pdf', 'pptx', 'docx', 'xlsx', 'jpg', 'png', 'mp3', 'wav', 'html', 'csv', 'json', 'xml'],
            label_visibility="visible",
            accept_multiple_files=False,
            help=t.get("drag_drop_text", "Dateien hierher ziehen und ablegen oder durchsuchen")
        )

        st.header(t["settings_header"])
        use_llm = st.toggle(t["use_llm_toggle"], value=False)
        
        # Dokumentsprache auswählen
        if use_llm:
            document_languages = {
                "auto": t["auto_detect"],
                "de": "Deutsch",
                "en": "English",
                "fr": "Français",
                "es": "Español",
                "it": "Italiano",
                "nl": "Nederlands",
                "pt": "Português",
                "ru": "Русский",
                "zh": "中文",
                "ja": "日本語"
            }
            
            doc_lang = st.selectbox(
                t["document_language"],
                options=list(document_languages.keys()),
                format_func=lambda x: document_languages[x],
                index=0,
                help=t["document_language_help"]
            )
        else:
            doc_lang = "auto"

        st.header(t["llm_provider_header"])
        llm_provider = st.radio(t["select_llm_provider"], ["Local", "OpenAI"], index=0)

        # Add configuration options for each provider
        custom_api_key = None
        local_llm_url = None
        
        if llm_provider == "OpenAI":
            custom_api_key = st.text_input(
                t["openai_api_key"],
                type="password",
                help=t["api_key_help"],
                value=os.getenv('OPENAI_API_KEY', '')
            )
        else:  # Local LLM
            local_llm_url = st.text_input(
                t["local_llm_url"],
                value="http://127.0.0.1:1234/v1/chat/completions",
                help=t["local_llm_help"]
            )

        if st.button(t["clear_cache"]):
            clear_cache()
            st.success(t["cache_cleared"])
        
        st.markdown(f"""
        ### {t["supported_formats"]}
        - PDF ({t.get("extract_images_text", "Extrahiert Text und Bilder und beschreibt Bilder inline, wenn LLM aktiviert ist")})
        - PPTX
        - DOCX
        - XLSX
        - Images
        - Audio
        - HTML
        - Text
        """)

    if uploaded_file:
        with st.spinner(t["processing"]):
            try:
                text_content = process_document(
                    uploaded_file, 
                    use_llm=use_llm, 
                    llm_provider=llm_provider, 
                    custom_api_key=custom_api_key,
                    local_llm_url=local_llm_url,
                    ui_lang=lang,
                    doc_lang=doc_lang
                )
                
                st.header(t["analysis_results"])
                tab1, tab2, tab3 = st.tabs([t["tab_extracted"], t["tab_info"], t["tab_debug"]])
                
                with tab1:
                    st.text_area(t["tab_extracted"], text_content, height=600)
                    st.download_button(
                        t["download_button"],
                        text_content,
                        file_name=f"{uploaded_file.name}_extracted.md",
                        mime="text/plain"
                    )
                
                with tab2:
                    st.json({
                        "Filename": uploaded_file.name,
                        "File size (KB)": f"{uploaded_file.size / 1024:.2f}",
                        "File type": uploaded_file.type
                    })
                
                with tab3:
                    if debug_logs:
                        st.write(t["debug_logs_title"])
                        for log in debug_logs:
                            st.write(log)
                    else:
                        st.write(t["no_debug_logs"])
            except Exception as e:
                st.error(f"{t['error_processing']} {str(e)}")
                if debug_logs:
                    st.write(t["debug_logs_title"])
                    for log in debug_logs:
                        st.write(log)
    else:
        st.info(t["upload_prompt"])

if __name__ == "__main__":
    main()
