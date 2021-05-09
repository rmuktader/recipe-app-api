web_server=$(docker ps -a -q --filter name=ps_app --format='{{.ID}}')
if [ $web_server ]
then
  docker rm -f $web_server
fi

db_server=$(docker ps -a -q --filter name=docker_db_1 --format='{{.ID}}')
if [ $db_server ]
then
  docker rm -f $db_server
fi