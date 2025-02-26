import os
import zipfile
import io
import requests
import shutil
import gdown
from acdh_tei_pyutils.tei import TeiReader
from config import (
    CONVERSION_DOMAIN,
    TMP_DIR,
    SOURCE_DOCX_URLS,
    SOURCE_DOCX_FILES,
    SOURCE_XML_FILES,
)

shutil.rmtree(TMP_DIR, ignore_errors=True)
os.makedirs(TMP_DIR, exist_ok=True)

for url, docx_file, xml_file in zip(
    SOURCE_DOCX_URLS, SOURCE_DOCX_FILES, SOURCE_XML_FILES
):
    print(f"start download from {url}")
    gdown.download(url, docx_file)
    print(f"saved {docx_file}")

    print(f"posting {docx_file} to {CONVERSION_DOMAIN}")
    headers = {
        "accept": "application/octet-stream",
    }
    params = {
        "properties": '<conversions><conversion index="0"><property id="oxgarage.getImages">false</property><property id="oxgarage.getOnlineImages">false</property><property id="oxgarage.lang">en</property><property id="oxgarage.textOnly">true</property><property id="pl.psnc.dl.ege.tei.profileNames">default</property></conversion></conversions>',  # noqa
    }
    files = {"fileToConvert": open(docx_file, "rb")}
    response = requests.post(
        f"{CONVERSION_DOMAIN}ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml",  # noqa
        params=params,
        headers=headers,
        files=files,
    )
    try:
        data = response.content.decode("utf-8")
    except UnicodeDecodeError:
        ZIP_DIR = os.path.join(TMP_DIR, "zip")
        shutil.rmtree(ZIP_DIR, ignore_errors=True)
        os.makedirs(ZIP_DIR, exist_ok=True)
        print(f"Content-Type: {response.headers['Content-Type']}")
        zip_file = io.BytesIO(response.content)

        # Unzip the content
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(ZIP_DIR)
        # Read the TEI
        with open(os.path.join(ZIP_DIR, "tei.xml"), "r", encoding="utf-8") as fp:
            data = fp.read()
        # clean up
        shutil.rmtree(ZIP_DIR, ignore_errors=True)

    data = data.replace("heading=h.", "heading_h_")
    data = data.replace('xml:id="', 'xml:id="xmlid__')
    print(f"saving result as {xml_file}")
    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(data)

    doc = TeiReader(data)
