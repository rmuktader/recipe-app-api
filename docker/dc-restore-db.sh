source .env
echo "Restoring database '${DB_NAME}' from at '${DB_DUMP}' as user '${DB_USERNAME}'"

docker-compose run web bash -c 'echo "Environment started"' &&
gunzip -c ${DB_DUMP} \
| docker-compose exec -T db psql -U ${DB_USERNAME} ${DB_NAME}