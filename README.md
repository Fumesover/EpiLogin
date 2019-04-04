# EPILOGIN: Easy discord auth using microsoft oauth2

This is a discord bot that allow you to authentificate users using their emails.

### Run this bot localy

```bash
# First get a postgresql server running on your computer
$ docker run --rm -p 5432:5432 postgres

# Edit database url in config file
# url: postgres://postgres@localhost/postgres
$ $EDITOR config.yml

# The project run on python3.6, so stay explicit
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python3 -m pip install -r requirements.txt

# Simply run the bot by doing
python main.py
```
