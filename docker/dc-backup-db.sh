source .env
echo "Backing up database '${DB_NAME}' as user '${DB_USERNAME}' at '${DB_DUMP}'"
docker-compose run web bash -c 'echo "Environment started"' &&
docker-compose exec db bash -c \
"pg_dump --clean --username ${DB_USERNAME} ${DB_NAME}" | gzip -9 > ${DB_DUMP}
