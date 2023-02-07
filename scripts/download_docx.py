import requests
import shutil
import os
import gdown
from acdh_tei_pyutils.tei import TeiReader
from config import (
    CONVERSION_DOMAIN,
    TMP_DIR,
    SOURCE_DOCX,
    SOURCE_DOCX_URL,
    SOURCE_XML
)

shutil.rmtree(TMP_DIR, ignore_errors=True)
os.makedirs(TMP_DIR, exist_ok=True)

print(f"start download from {SOURCE_DOCX_URL}")
gdown.download(SOURCE_DOCX_URL, SOURCE_DOCX)
print(f"saved {SOURCE_DOCX}")


print(f"posting {SOURCE_DOCX} to {CONVERSION_DOMAIN}")
headers = {
    "accept": "application/octet-stream",
}
params = {
    "properties": '<conversions><conversion index="0"><property id="oxgarage.getImages">false</property><property id="oxgarage.getOnlineImages">false</property><property id="oxgarage.lang">en</property><property id="oxgarage.textOnly">true</property><property id="pl.psnc.dl.ege.tei.profileNames">default</property></conversion></conversions>',
}
files = {"fileToConvert": open(SOURCE_DOCX, "rb")}
response = requests.post(
    f"{CONVERSION_DOMAIN}ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml",
    params=params,
    headers=headers,
    files=files,
)
data = response.content.decode("utf-8")
data = data.replace("heading=h.", "heading_h_")
data = data.replace('xml:id="', 'xml:id="xmlid__')
print(f"saving result as {SOURCE_XML}")
with open(SOURCE_XML, "w") as f:
    f.write(data)

doc = TeiReader(data)
