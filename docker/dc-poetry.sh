#!/bin/bash

docker-compose run poetry poetry "$@"
read -p "Do you want to rebuild web image (highly recommended after adding or removing deps)? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker-compose build web
fi