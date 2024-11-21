import os

CONVERSION_DOMAIN = "https://teigarage.tei-c.org/"
TMP_DIR = os.path.join(".", "tmp")
SOURCE_DOC_GID = "1Dl4IPqu6OQnf1AwI03rNsx2DJDtaA2NB"
SOURCE_DOCX_FILENAME = "source.docx"
SOURCE_DOCX_URL = f"https://drive.google.com/uc?id={SOURCE_DOC_GID}"
SOURCE_DOCX = os.path.join(TMP_DIR, SOURCE_DOCX_FILENAME)
SOURCE_XML = SOURCE_DOCX.replace(".docx", ".xml")
print(SOURCE_XML)
TEI_DIR = os.path.join(".", "tei")
DOCUMENT_URL = "https://raw.githubusercontent.com/grocerist/grocerist-data/main/json_dumps/documents.json"
