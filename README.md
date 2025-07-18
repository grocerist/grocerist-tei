# grocerist-tei
Repo for conversion and storing transcriptions from DOCX as XML/TEI files


## usage

* `python scripts/download_docx.py` downloads docx from gdrive, converts it via oxgarage into an XML/TEI Document and saves it into `tmp/source.xml`
* `python scripts/split.py` splits `tmp/source.xml` in single XML/TEI files and enriches them with baserow-data


## Licensing

All code unless otherwise noted is licensed under the terms [MIT License](https://opensource.org/licenses/MIT).

For licensing information of the data in this repository, please look into the individual folders/files for further information.


## ARCHE

### secrets
* copy `dev.env` to `.secrets` and modify to you needs
* adapt [`arche/arche_constants.ttl`](arche/arche_constants.ttl), [`arche/repo_objects_constants.ttl`](arche/repo_objects_constants.ttl), [`arche/title-image.jpg`](arche/title-image.jpg), and [`arche/make_arche_rdf.py`](arche/make_arche_rdf.py) to your needs (those files are obvisiously copied from another project)
