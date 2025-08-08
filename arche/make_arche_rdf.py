import glob
import os
import shutil
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext
from rdflib import Namespace, URIRef, RDF, Graph, Literal, XSD

to_ingest = "to_ingest"
os.makedirs(to_ingest, exist_ok=True)
g = Graph().parse("arche/arche_constants.ttl")
g_repo_objects = Graph().parse("arche/repo_objects_constants.ttl")
TOP_COL_URI = URIRef("https://id.acdh.oeaw.ac.at/grocerist")
APP_URL = "https://grocerist.acdh.oeaw.ac.at/"

ACDH = Namespace("https://vocabs.acdh.oeaw.ac.at/schema#")
COLS = [ACDH["TopCollection"], ACDH["Collection"], ACDH["Resource"]]
COL_URIS = set()


files = sorted(glob.glob("tei/*.xml"))
# files = files[30:50]
for x in tqdm(files):
    doc = TeiReader(x)
    cur_doc_id = os.path.split(x)[-1]

    # TEI/XML Document
    cur_doc_uri = URIRef(f"{TOP_COL_URI}/{cur_doc_id}")
    g.add((cur_doc_uri, RDF.type, ACDH["Resource"]))
    g.add((cur_doc_uri, ACDH["isPartOf"], URIRef(f"{TOP_COL_URI}/documents")))
    # g.add(
    #     (
    #         cur_doc_uri,
    #         ACDH["hasUrl"],
    #         Literal(f'{APP_URL}{cur_doc_id.replace(".xml", ".html")}'),
    #     )
    # )
    g.add(
        (
            cur_doc_uri,
            ACDH["hasLicense"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archelicenses/cc-by-4-0"),
        )
    )

    # title
    title = extract_fulltext(doc.any_xpath(".//tei:titleStmt/tei:title[@level='a']")[0])
    # make lang undefined, because the title is the shelfmark?
    # or sth like title to the title, then it would be English
    g.add(
        (
            cur_doc_uri,
            ACDH["hasTitle"],
            Literal(f"{title}", lang="und"),
        )
    )
    g.add(
        (
            cur_doc_uri,
            ACDH["hasCategory"],
            URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
        )
    )

    # add date
    # do we add sth else, like the century if there is no iso-date?
    try:
        date = (
            doc.any_xpath(".//tei:origin/@when-iso")[0]
        )
    except IndexError:
        date = False
    if date:
        g.add(
            (
                cur_doc_uri,
                ACDH["hasCoverageStartDate"],
                Literal(date, datatype=XSD.date),
            )
        )


    # hasCreator
    for y in doc.any_xpath(".//tei:persName[@role='acdh:hasCreator'][@key]"):
        editor_name = extract_fulltext(y)
        editor_id = y.attrib["key"]
        if editor_id.startswith("https://orcid.org"):
            creator_uri = URIRef(editor_id)
            g.add((creator_uri, RDF.type, ACDH["Person"]))
            g.add((creator_uri, ACDH["hasTitle"], Literal(editor_name, lang="und")))
            g.add((cur_doc_uri, ACDH["hasCreator"], creator_uri))

    # hasExtent
    nr_of_pages = len(doc.any_xpath(".//tei:facsimile/tei:graphic"))
    if nr_of_pages > 1:
        g.add(
            (
                cur_doc_uri,
                ACDH["hasExtent"],
                Literal(f"{nr_of_pages} pages", lang="en"),
            )
        )
    else:
        g.add(
            (cur_doc_uri, ACDH["hasExtent"], Literal(f"{nr_of_pages} page", lang="en"))
        )

for x in COLS:
    for s in g.subjects(None, x):
        COL_URIS.add(s)

for x in COL_URIS:
    for p, o in g_repo_objects.predicate_objects():
        g.add((x, p, o))

print("writing graph to file")
# g.serialize("html/arche.ttl")
# g.serialize("to_ingest/arche.ttl")
g.serialize("arche.ttl")

files_to_ingest = glob.glob("./data/*/*.xml")
print(f"copying {len(files_to_ingest)} into {to_ingest}")
for x in files_to_ingest:
    _, tail = os.path.split(x)
    new_name = os.path.join(to_ingest, tail)
    shutil.copy(x, new_name)
