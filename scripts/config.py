import os

CONVERSION_DOMAIN = "https://teigarage.tei-c.org/"
TMP_DIR = os.path.join(".", "tmp")
SOURCE_DOC_GIDS = [
    "1Dl4IPqu6OQnf1AwI03rNsx2DJDtaA2NB",
    "1RC8H43g0FOCpfNJX8n9ZA1ck4FLfl90W"
]
SOURCE_DOCX_FILENAMES = [f"source_{i}.docx" for i in range(len(SOURCE_DOC_GIDS))]
SOURCE_DOCX_URLS = [f"https://drive.google.com/uc?id={gid}" for gid in SOURCE_DOC_GIDS]
SOURCE_DOCX_FILES = [
    os.path.join(TMP_DIR, filename) for filename in SOURCE_DOCX_FILENAMES
]
SOURCE_XML_FILES = [
    docx_file.replace(".docx", ".xml") for docx_file in SOURCE_DOCX_FILES
]

TEI_DIR = os.path.join(".", "tei")
DOCUMENT_URL = "https://raw.githubusercontent.com/grocerist/grocerist-data/main/json_dumps/documents.json"
