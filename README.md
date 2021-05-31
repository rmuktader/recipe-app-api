# django_boilerplate
Boilerplate code to jumpstart Django development. It's packages are maintained using Poetry, it runs on on local and on Docker. It comes with helper scripts that can be run from VS Code.

---

## Installation

Modify local.env and .env files with unique DOCKER_DB_EXTERNAL_PORT value so it doesn't clash with another ports that are in use on local. Change DB_NAME and DB_HOST values in local.env and .env files to something that reflects the project.

```bash
pyenv local 3.9.1
poetry shell
poetry install
docker-compose build
./dc-manage.sh migrate
```

Open the project folder in VS Code. Click on "Run and Debug" on left column and either choose "docker:runserver" or "local:runserver"


