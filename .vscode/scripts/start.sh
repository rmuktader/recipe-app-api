cd docker
old_containers=$(docker ps -a -q --filter name=ps_app --format='{{.ID}}')

if [ ! -z "$old_containers" ]
then
    echo "Removing old containers..."
    docker rm -f $old_containers
fi

docker-compose run --name ps_app -d -p 8000:8000 -p 3000:3000 web bash -c 'python -m ptvsd --host 0.0.0.0 --port 3000 --wait manage.py runserver --noreload 0.0.0.0:8000'
sleep 2
