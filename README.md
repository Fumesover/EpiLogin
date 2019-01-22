# EPILOGIN: Easy github auth using emails

This is a discord bot that allow you to authentificate users using their emails.

### Run this bot localy

```bash
# First get a postgresql server running on your computer
$ docker run --rm -p 5432:5432 postgres

# Edit database url in config file
url: postgres://postgres@localhost/postgres

# The project run on python3.6, so stay explicit
python3.6 -m venv .venv
source .venv/bin/activate
python3.6 -m pip install -r requirements.txt

# Simply run the bot by doing
python3.6 main.py
```

### Backup and restore

Backup:
> docker-compose exec epilogin-db pg_dump postgres -U postgres  > backup.sql

Restore:
> cat backup.sql | docker exec -i $(docker-compose ps -q epilogin-db) psql -U postgres
