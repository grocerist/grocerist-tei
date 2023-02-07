import os
import shutil
from acdh_tei_pyutils.tei import TeiReader

from config import TEI_DIR, SOURCE_XML

shutil.rmtree(TEI_DIR, ignore_errors=True)
os.makedirs(TEI_DIR, exist_ok=True)

doc = TeiReader(SOURCE_XML)
nsmap = doc.nsmap


items = doc.any_xpath('.//tei:body//tei:div')
for x in items:
    doc_id = x.xpath('.//@target[1]')[0].split('/')[-1]
    print(doc_id)
