import glob
import os
import shutil
from tqdm import tqdm
# from acdh_cidoc_pyutils import extract_begin_end
from acdh_tei_pyutils.tei import TeiReader
from acdh_tei_pyutils.utils import extract_fulltext, make_entity_label, get_xmlid
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
"""
# following code is needed because different (?) place entities share the same geonames-id
# this leads to acdh:Place objects with more than one acdh:hasTitle properties, which is not allowed

doc = TeiReader("./data/indices/listplace.xml")
lookup_dict = {}
for x in doc.any_xpath(".//tei:place[@xml:id and ./tei:idno[@type='geonames']]"):
    label = make_entity_label(x.xpath("./*[1]")[0])[0]
    entity_id = x.xpath("./*[@type='geonames']/text()")[0]
    lookup_dict[entity_id] = label

# end of this annoying workaround

# and the same for persons of course ...

doc = TeiReader("./data/indices/listperson.xml")
for x in doc.any_xpath(".//tei:person[@xml:id and ./tei:idno[@type='gnd']]"):
    label = make_entity_label(x.xpath("./*[1]")[0])[0]
    entity_id = x.xpath("./*[@type='gnd']/text()")[0]
    lookup_dict[entity_id] = label

# end of this annoying workaround
"""
"""
mandatory info for resources:
- hasTitle °
- hasIdentifier
- hasCategory °
- hasMetadataCreator
- hasLicensor
- hasRightsHolder
- hasLicense  °
- isPartOf °
curation related:
- hasDepositor
- hasAvailableDate
- hasHosting
recommended:
- hasDescription
- hasLanguage
- hasExtent
- hasUpdatedDate
- hasPrincipalInvestigator
- hasFormat
- hasCurator
- hasSubmissionDate
- hasAcceptedDate
- hasTransferDate
"""
files = sorted(glob.glob("tei/*.xml"))
# files = files[30:50]
for x in tqdm(files):
    doc = TeiReader(x)
    # hä? find out what cur_col_id is supposed to be, I'm assuming there was some original function different from this code
    cur_col_id = os.path.split(x)[-1].replace(".xml", "")
    cur_doc_id = f"{cur_col_id}.xml"

    # TEI/XML Document
    cur_doc_uri = URIRef(f"{TOP_COL_URI}/{cur_doc_id}")
    g.add((cur_doc_uri, RDF.type, ACDH["Resource"]))
    g.add((cur_doc_uri, ACDH["isPartOf"], URIRef(f"{TOP_COL_URI}/editions")))
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

    # start/end date
    # try:
    #     start, end = extract_begin_end(
    #         doc.any_xpath(".//tei:correspAction[@type='sent']/tei:date")[0]
    #     )
    # except IndexError:
    #     start, end = False, False
    # if start:
    #     g.add(
    #         (
    #             cur_doc_uri,
    #             ACDH["hasCoverageStartDate"],
    #             Literal(start, datatype=XSD.date),
    #         )
    #     )
    # if end:
    #     g.add(
    #         (cur_doc_uri, ACDH["hasCoverageEndDate"], Literal(start, datatype=XSD.date))
    #     )

    # actors (persons):
    for y in doc.any_xpath(
        ".//tei:back//tei:person[@xml:id and ./tei:idno[@type='wikidata'] or tei:idno[@type='gnd']]"
    ):
        xml_id = get_xmlid(y)
        try:
            entity_id = y.xpath("./*[@type='gnd']/text()")[0]
        except IndexError:
            try:
                entity_id = y.xpath("./*[@type='wikidata']/text()")[0]
            except IndexError:
                continue
        entity_title = lookup_dict[entity_id]
        entity_uri = URIRef(entity_id)
        g.add((entity_uri, RDF.type, ACDH["Person"]))
        # g.add(
        #     (
        #         entity_uri,
        #         ACDH["hasUrl"],
        #         Literal(f"{APP_URL}{xml_id}.html", datatype=XSD.anyURI),
        #     )
        # )
        g.add((entity_uri, ACDH["hasTitle"], Literal(entity_title, lang="und")))
        g.add((cur_doc_uri, ACDH["hasActor"], entity_uri))

    # spatial coverage:
    for y in doc.any_xpath(
        ".//tei:back//tei:place[@xml:id and ./tei:idno[@type='geonames']]"
    ):
        xml_id = get_xmlid(y)
        entity_id = y.xpath("./*[@type='geonames']/text()")[0]
        entity_title = lookup_dict[entity_id]
        entity_uri = URIRef(entity_id)
        g.add((entity_uri, RDF.type, ACDH["Place"]))
        # g.add((entity_uri, ACDH["hasUrl"], Literal(f"{APP_URL}{xml_id}", datatype=XSD.anyURI)))
        g.add((entity_uri, ACDH["hasTitle"], Literal(entity_title, lang="und")))
        g.add((cur_doc_uri, ACDH["hasSpatialCoverage"], entity_uri))

    # hasCreator
    # wouldn't this need to be more specific? like persName from the respStmt with the role "acdh:hasCreator"?
    for y in doc.any_xpath(".//tei:name[@key]"):
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
            (cur_doc_uri, ACDH["hasExtent"], Literal(f"{nr_of_pages} pages", lang="en"))
        )

    # indices and meta
    # for y in ["indices", "meta"]:
    #     for x in glob.glob(f"./data/{y}/*.xml"):
    #         doc = TeiReader(x)
    #         cur_doc_id = os.path.split(x)[-1]
    #         cur_doc_uri = URIRef(f"{TOP_COL_URI}/{cur_doc_id}")
    #         g.add((cur_doc_uri, RDF.type, ACDH["Resource"]))
    #         g.add((cur_doc_uri, ACDH["isPartOf"], URIRef(f"{TOP_COL_URI}/{y}")))
    #         g.add(
    #             (
    #                 cur_doc_uri,
    #                 ACDH["hasLicense"],
    #                 URIRef("https://vocabs.acdh.oeaw.ac.at/archelicenses/cc-by-4-0"),
    #             )
    #         )
    #         title = extract_fulltext(doc.any_xpath(".//tei:titleStmt/tei:title[1]")[0])
    #         g.add(
    #             (
    #                 cur_doc_uri,
    #                 ACDH["hasTitle"],
    #                 Literal(f"{title}", lang="de"),
    #             )
    #         )
    #         g.add(
    #             (
    #                 cur_doc_uri,
    #                 ACDH["hasCategory"],
    #                 URIRef("https://vocabs.acdh.oeaw.ac.at/archecategory/text/tei"),
    #             )
    #         )

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
