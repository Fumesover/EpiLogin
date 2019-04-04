import logging
import json
import requests
from requests.auth import HTTPBasicAuth

BAN_TYPES = (
    ('group', 'GROUP'),
    ('login', 'LOGIN'),
    ('user', 'USER'),
)

# TODO: AUTH TOKEN (Authorization: Token 7dd94922cbc44ac9745a2203cec34233dcc7592d)

# get all parameters if the api is in multi pages
def fetch_paginate(next):
    output = []

    while next:
        r = requests.get(url)

        if r.status_code != 200:
            return None

        data = r.json()

        output += data['results']
        next = data['next']

    return output

def get_member(discord_id):
    url = "{}/api/members/{}/".format(config['website']['url'], discord_id)
    r = requests.get(url)

    if r.status_code == 200:
        return r.json()
    else:
        return None

def create_member(discord_id):
    url = "{}/api/members/".format(config['website']['url'])
    r = requests.post(url, {'id': discord_id})

    if r.status_code == 200:
        return r.json()
    else:
        return None

def get_ids(login):
    url = "{}/api/members/?login={}".format(config['website']['url'], login)
    return fetch_paginate(url)

def get_groups(login='', group=''):
    url = "{}/api/groups/?login={}&group={}".format(config['website']['url'], login, group)
    return fetch_paginate(url)

def get_bans(server, login='', group=''):
    url = "{}/api/bans/?server={}&type={}&value={}".format(server, login, group)
    return fetch_paginate(url)

def get_updates():
    url = "{}/api/updates/".format(config['website']['url'])
    return fetch_paginate(url)

def del_updates(ids):
    for id in ids:
        url = "{}/api/updates/{}/".format(config['website']['url'], id)
        r.delete(url)

def __format_bans(server):
    ban_set = server.pop('ban_set')
    server['bans'] = {
        'group': [],
        'login': [],
        'user':  [],
    }

    for ban in ban_set:
        server['bans'][ban['type']] = ban['value']

def __format_ranks(server):
    rank_set = server.pop('rank_set')
    server['ranks'] = {
        'classic':   {},
        'confirmed': [],
        'banned':    [],
    }

    for rank in rank_set:
        type       = rank.pop('type')
        discord_id = rank.pop('discord_id')
        name       = rank.pop('name')

        if type == 'classic':
            if not name in server['ranks'][type]:
                server['ranks'][type][name] = []
            server['ranks'][type][name].append(discord_id)
        else:
            server['ranks'][type].append(rank_id)

def update_conf_all():
    url = '{}/api/servers/'.format(config['website']['url'])
    data = fetch_paginate(url)

    if not data:
        return False

    new = {}

    for server in data:
        server_id = server.pop('id')
        new[server['id']] = server

        __format_ranks(server)
        __format_bans(server)

    config['servers'] = new

    return True

def update_conf(server_id):
    url = '{}/api/servers/{}/'.format(config['website']['url'], server_id)
    r = r.get(url)

    if r.status_code != 200:
        return False

    server = r.json()
    __format_ranks(server)
    __format_bans(server)
    config['servers'][server_id] = server

    return True

def on_member_remove(member_id):
    pass

def on_member_join(member_id):
    pass

def on_guild_join(guild_id):
    url = "{}/api/servers/".format(config['website']['url'])
    r = requests.post(url, {'id': guild_id})
