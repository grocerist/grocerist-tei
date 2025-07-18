#/bin/bash

if [ "${TITLEIMAGE}" != "" ] ; then
  echo "deleting ${TITLEIMAGE} from ${ARCHE}"
  docker run --rm \
    --network="host" \
    --entrypoint arche-delete-resource \
    acdhch/arche-ingest \
    ${TITLEIMAGE} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD}
fi

if [ "${PROJECTID}" != "" ] ; then
  echo "deleting ${PROJECTID} from ${ARCHE}"
  docker run --rm \
    --network="host" \
    --entrypoint arche-delete-resource \
    acdhch/arche-ingest \
    ${PROJECTID} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD}  --references
fi

echo ""
echo "delete ${TOPCOLID} from ${ARCHE}"
docker run --rm \
  --network="host" \
  --entrypoint arche-delete-resource \
  acdhch/arche-ingest \
  ${TOPCOLID} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD} --recursively