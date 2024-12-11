import os
import shutil
import lxml.etree as ET
import jinja2
import requests
from acdh_tei_pyutils.tei import TeiReader
import copy


from config import TEI_DIR, SOURCE_XML, DOCUMENT_URL

nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
}

templateLoader = jinja2.FileSystemLoader(searchpath="./scripts/templates")
templateEnv = jinja2.Environment(
    loader=templateLoader, trim_blocks=True, lstrip_blocks=True
)
template = templateEnv.get_template("document.j2")

print(f"fetching document-info from {DOCUMENT_URL}")
r = requests.get(DOCUMENT_URL)
data = r.json()

shutil.rmtree(TEI_DIR, ignore_errors=True)
os.makedirs(TEI_DIR, exist_ok=True)

doc = TeiReader(SOURCE_XML)
nsmap = doc.nsmap


items = doc.any_xpath(".//tei:body//tei:div")
first_pass = True
for x in items:
    object = {}
    doc_refs = x.xpath(".//tei:head//@target", namespaces=nsmap)
    section_refs = x.xpath(".//tei:p//@target", namespaces=nsmap)
    for ref in doc_refs:
        if section_refs and first_pass:
            for section in section_refs:
                p_element = x.xpath(
                    f"./tei:p/tei:ref[@target='{section}']", namespaces=nsmap
                )[0].getparent()
                parent = p_element.getparent()
                div = ET.Element("div")
                div.set("type", "section")
                parent.replace(p_element, div)
                div.append(p_element)
                next_sibling = div.getnext()
                while next_sibling is not None and not next_sibling.xpath(
                    ".//@target", namespaces=nsmap
                ):
                    sibling_to_move = next_sibling
                    next_sibling = div.getnext()
                    div.append(sibling_to_move)
            first_pass = False

        doc_id = ref.split("/")[-1]
        file_name = f"{doc_id}.xml"
        object["doc_id"] = doc_id
        doc_cur_nr = doc_id.split("__")[-1]
        object["file_name"] = file_name
        object["body"] = ET.tostring(x).decode("utf-8")
        context = {}
        context["object"] = object
        context["info"] = data[doc_cur_nr]
        xml_data = template.render(context).replace('style="font-size:12pt"', "")
        doc = TeiReader(xml_data)
        doc.tree_to_file(os.path.join(TEI_DIR, file_name))
