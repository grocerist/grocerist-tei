#/bin/bash

python3 -m pip install --user cvdupdate && cvd update
echo "run virus scan for for ${TOPCOLID}"

docker run \
  --rm \
  -v ~/.cvdupdate/database/:/var/lib/clamav \
  -v ${PWD}/to_ingest:/data \
  --entrypoint clamscan \
  acdhch/arche-ingest \
  --recursive --infected /data