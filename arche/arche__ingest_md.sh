#/bin/bash
echo "creating arche-metadata"
python arche/make_arche_rdf.py
echo "ingest metadata for for ${TOPCOLID} into ${ARCHE}"
docker run --rm \
  -v ${PWD}/to_ingest:/data \
  --network="host" \
  --entrypoint arche-import-metadata \
  acdhch/arche-ingest \
  /data/arche.ttl ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD}