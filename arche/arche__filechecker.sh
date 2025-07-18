#/bin/bash
echo "run filechecker for for ${TOPCOLID}"
rm -rf ${PWD}/fc_out && mkdir ${PWD}/fc_out
mv ${PWD}/to_ingest/arche.ttl ${PWD}/to_ingest/arche.txt 
docker run \
  --rm \
  --network="host" \
  -v ${PWD}/fc_out:/reports \
  -v ${PWD}/to_ingest:/data \
  --entrypoint arche-filechecker \
  acdhch/arche-ingest \
  --overwrite --skipWarnings /data /reports
mv ${PWD}/to_ingest/arche.txt ${PWD}/to_ingest/arche.ttl
