# grocerist-tei
Repo for conversion and storing transcriptions from DOCX as XML/TEI files


## usage

* `python scripts/download_docx.py` downloads docx from gdrive, converts it via oxgarage into an XML/TEI Document and saves it into `tmp/source.xml`
* `python scripts/split.py` splits `tmp/source.xml` in single XML/TEI files and enriches them with baserow-data


## Licensing

All code unless otherwise noted is licensed under the terms [MIT License](https://opensource.org/licenses/MIT).

For licensing information of the data in this repository, please look into the individual folders/files for further information.
