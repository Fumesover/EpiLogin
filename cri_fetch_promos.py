import urllib.request
import json
import sqlite3
import argparse
import re
import discord

import database
import logging
import utils

regexlogin = '([a-zA-Z0-9_.+-]+)@(?:(?:[a-zA-Z0-9-]+\\.)?[a-zA-Z]+\\.)?epita\\.fr'

async def update_groups(client, database, login, new_groups, config):
    prev_groups = await database.get_groups(login)

    to_add    = list(set(new_groups) - set(prev_groups))
    to_remove = list(set(prev_groups) - set(new_groups))

    await database.del_groups(login, to_remove)
    await database.add_groups(login, to_add)

    ids = await database.get_ids(login)
    for id in ids:
        for server in client.servers:
            member = server.get_member(str(id))
            if member:
                roles_to_remove = utils.ids_of_roles(client, server, to_remove)
                roles_to_add    = utils.ids_of_roles(client, server, to_add)

                if to_remove:
                    await utils.del_roles(client, config, member, roles_to_remove)
                if to_add:
                    await utils.give_roles(client, config, member, roles_to_add)

async def cri_fetch_promos(database, session_id, client, channel, config):
    l = logging.getLogger('discord.cri_fetch_promos.status')
    l.info('starting ...')

    urlapi = 'https://cri.epita.fr/api/users/?format=json&limit=100&offset=2800'

    while urlapi:
        l.info('getting ' + urlapi)
        req = urllib.request.Request(urlapi)
        req.add_header('Cookie', 'sessionid=' + session_id)
        r = urllib.request.urlopen(req)

        data = json.loads(r.read())

        urlapi = data['next']

        for person in data['results']:
            login = re.search(regexlogin, person['mail'])
            login = login.group(1) if login else None

            if not login:
                continue

            promo = person['promo']
            class_groups = person['class_groups']

            l.info(login + ' groups : ' + promo + ' ' + ' '.join(class_groups))

            await update_groups(client, database, login, [promo] + class_groups, config)

        if data['next']:
            await client.send_message(channel, str(data['next'].split('&')[2].split('=')[1]) + '/' + str(data['count']))
        else:
            await client.send_message(channel, str(data['count']) + '/' + str(data['count']))
