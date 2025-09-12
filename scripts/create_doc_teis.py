import os
import shutil
import lxml.etree as ET
import jinja2
import requests
from acdh_tei_pyutils.tei import TeiReader

# import copy


from config import TEI_DIR, SOURCE_XML_FILES, DOCUMENT_URL

nsmap = {
    "tei": "http://www.tei-c.org/ns/1.0",
}


def create_tei_document(doc_id, body_content, doc_info, template, has_transcript):
    # Create and save a TEI document using a Jinja2 template
    file_name = f"{doc_id}.xml"
    object_data = {"doc_id": doc_id, "file_name": file_name, "body": body_content}

    context = {"object": object_data, "info": doc_info, "has_transcript": has_transcript}

    xml_data = template.render(context)
    doc = TeiReader(xml_data)
    doc.tree_to_file(os.path.join(TEI_DIR, file_name))


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

# Process documents with a transcript
for source_xml in SOURCE_XML_FILES:
    doc = TeiReader(source_xml)
    nsmap = doc.nsmap

    items = doc.any_xpath(".//tei:body//tei:div")
    for x in items:
        # # for testing that the original text content wasn't modified during processing
        # y = copy.deepcopy(x)
        # ET.strip_tags(y, "*")
        # text_before = ET.tostring(y).decode("utf-8")

        first_pass = True
        object = {}
        doc_refs = x.xpath(".//tei:head//@target", namespaces=nsmap)
        section_refs = x.xpath(".//tei:p//@target", namespaces=nsmap)
        # for grocers with several stores, each store is a separate section
        # we use the sections for highlighting in the frontend
        for ref in doc_refs:
            try:

                # clean up refs because requests don't seem to help
                ref = ref.rstrip("/")
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

                # find and remove all style-related markup
                # remove all hi tags (but not their content)
                ET.strip_tags(x, "{http://www.tei-c.org/ns/1.0}hi")

                # find and remove all style attributes
                for el in x.xpath("//*[@style]", namespaces=nsmap):
                    el.attrib.pop("style")

                # # TEST continued
                # ET.strip_tags(x, "*")
                # text_after = ET.tostring(x).decode("utf-8")
                # if text_before != text_after:
                #     print("original text was changed during processing")

                doc_id = ref.split("/")[-1]
                doc_cur_nr = doc_id.split("__")[-1]
                body_content = ET.tostring(x).decode("utf-8")
                create_tei_document(doc_id, body_content, data[doc_cur_nr], template, has_transcript=True)
            except Exception as e:
                print(f"Error processing reference {ref} in {source_xml}: {e}")
                continue

# Process documents without transcripts
for doc_id, doc_info in data.items():
    # Check if this document already has a TEI file (i.e. was processed above)
    file_name = f"document__{doc_id}.xml"
    if not os.path.exists(os.path.join(TEI_DIR, file_name)):
        full_doc_id = f"document__{doc_id}"
        body_content = "<div><p>This document does not contain any groceries.</p></div>"
        create_tei_document(full_doc_id, body_content, doc_info, template, has_transcript=False)
