import discord
import asyncio
import logging
import json
import requests
from requests.auth import HTTPBasicAuth

import database
import utils
import logs
from database import BanType

def get_auth(config):
    return HTTPBasicAuth(config['website']['username'], config['website']['password'])

async def global_update(client, config, database, with_groups=False):
    l = logs.get_logger('hooks.global_update')
    l.info('preparing payload ...')

    data = {
        'servers': {},
        'members': {},
        'groups': [],
    }

    for server in client.servers:
        bans = await database.get_bans(server.id)
        banned = []
        for ban in bans:
            banned.append({
                'type': BanType(ban['type']).name,
                'data': ban['value']
            })

        data['servers'][server.id] = {
            'name': server.name,
            'id':   server.id,
            'bans': banned
        }

    members = {}
    for member in client.get_all_members():
        if member.id in members:
            members[member.id]['servers'].append(member.server.id)
        else:
            login = await database.get_login(member.id)

            members[member.id] = {
                'servers': [member.server.id],
                'name': member.name,
                'login': login if login else ''
            }

    data['members'] = members

    if with_groups:
        data['groups'] = []
        for e in await database.get_all_groups():
            data['groups'].append({
                'login': e['login'],
                'group': e['groupe']
            })

    l.info('payload ready, sending ...')

    r = requests.post(config['website']['url'] + '/servers/update', json=data, auth=get_auth(config))

    if r.status_code != 200:
        print(r.status_code)

    l.info('response : ' + str(r.status_code))

async def checkupdates(client, config, database):
    l = logs.get_logger('hooks.checkupdates')
    l.info('checking updates ...')

    r = requests.get(config['website']['url'] + '/servers/update', auth=get_auth(config))

    if r.status_code != 200:
        return

    data = r.json()
    confirmed = []

    for ban in data['ban']:
        server_id = ban['server']
        bantype   = BanType[ban['ban_type']]
        if not await database.check_ban(server_id, bantype, [ban['value']]):
            await database.ban(server_id, bantype, ban['value'])
            server = client.get_server(str(server_id))
            await logs.ban(client, config, server, bantype, [ban['value']])
        confirmed.append(ban['pk'])

    l.info('bans: done (' + str(len(confirmed)) + ')')

    for unban in data['unban']:
        server_id = unban['server']
        bantype   = BanType[unban['ban_type']]
        if await database.check_ban(server_id, bantype, [unban['value']]):
            await database.unban(server_id, bantype, unban['value'])
            server = client.get_server(str(server_id))
            await logs.unban(client, config, server, bantype, [unban['value']])
        confirmed.append(unban['pk'])

    l.info('unbans: done (' + str(len(confirmed)) + ')')

    for addgroup in data['addgroup']:
        groups = await database.get_groups(addgroup['login'])
        if not addgroup['value'] in groups:
            await database.add_groups(addgroup['login'], [addgroup['value']])
        confirmed.append(addgroup['pk'])

    l.info('addgroups: done (' + str(len(confirmed)) + ')')

    for delgroup in data['delgroup']:
        groups = await database.get_groups(delgroup['login'])
        if delgroup['value'] in groups:
            await database.del_groups(delgroup['login'], [delgroup['value']])
        confirmed.append(delgroup['pk'])

    l.info('delgroups: done (' + str(len(confirmed)) + ')')

    if confirmed:
        r = requests.delete(config['website']['url'] + '/servers/update', data=json.dumps({'pk':confirmed}), auth=get_auth(config))
        l.info('sync with server : ' + str(r.status_code))

async def hooksthread(client, config, database, with_groups=False):
    l = logs.get_logger('hooks.started')
    l.info('hook started')

    await client.wait_until_ready()

    await checkupdates(client, config, database)
    await global_update(client, config, database, with_groups=with_groups)

    while not client.is_closed:
        try:
            await checkupdates(client, config, database)
        except:
            pass

        await asyncio.sleep(30)

async def push(config, data):
    r = requests.post(config['website']['url'] + '/servers/push', json=data, auth=get_auth(config))
