import discord
import asyncio
import logging
import json
import requests

import utils
import api

async def checkupdates(client, config):
    data = api.get_updates(config)
    confirmed = []

    async def certify(data):
        user_id    = int(data['value'])
        user_login = data['login']

        for guild in client.guilds:
            m = guild.get_member(user_id)
            if m:
                await utils.on_certify(config, m, user_login)
        confirmed.append(data['id'])
    #TODO: SEND MESSAGE TO USER

    async def ban(data):
        guild_id = data['server']
        guild = client.get_guild(guild_id)
        if not guild or not config['servers'][guild_id]['is_active']:
            return

        async def ban_user(data):
            try:
                user_id = int(data['value'])
            except ValueError:
                return
            m    = guild.get_member(user_id)
            if m:
                to_set = [] + config['servers'][guild_id]['ranks']['banned']
                await utils.set_roles(config, m, to_set)

        async def ban_login(data):
            ids = api.get_ids(config, data['login'])
            for id in ids:
                if 'id' in id:
                    await ban_user({'value': str(id['id'])})

        async def ban_group(data):
            users = api.get_groups(config, group=data['value'])
            for user in users:
                await ban_login(user)

        handler = {
            'user': ban_user,
            'group': ban_group,
            'login': ban_login,
        }

        if data['ban_type'] in handler:
            await handler[data['ban_type']](data)
            confirmed.append(data['id'])

    async def unban(data):
        guild_id = data['server']
        guild = client.get_guild(guild_id)
        if not guild or not config['servers'][guild_id]['is_active']:
            return

        async def unban_user(data):
            try:
                user_id = int(data['value'])
            except ValueError:
                return
            m    = guild.get_member(user_id)
            if m:
                await utils.on_member_join(client, m, config)

        async def unban_login(data):
            ids = api.get_ids(config, data['login'])
            for id in ids:
                if 'id' in id:
                    await unban_user({'value': str(id['id'])})

        async def unban_group(data):
            users = api.get_groups(config, group=data['value'])
            for user in users:
                await unban_login(user)

        handler = {
            'user': unban_user,
            'group': unban_group,
            'login': unban_login,
        }

        if data['ban_type'] in handler:
            await handler[data['ban_type']](data)
            confirmed.append(data['id'])

    async def addgroup(data):
        login = data['login']
        ids = api.get_ids(config, login)
        for user in ids:
            if user['id']:
                for guild in client.guilds:
                    m = guild.get_member(user['id'])
                    if m:
                        await utils.on_certify(config, m, login)
        confirmed.append(data['id'])

    handelers = {
        'certify': certify,
        'ban': ban,
        'unban': unban,
        'addgroup': addgroup,
        'delgroup': addgroup,
    }

    for update in data:
        if 'type' in update and update['type'] in handelers:
            await handelers[update['type']](update)
        else:
            print('wtf ?', update)

    print('confirmed', confirmed)

    if confirmed:
        r = api.del_updates(config, confirmed)

async def hooksthread(client, config):
    await client.wait_until_ready()
    while not 'servers' in config:
        await asyncio.sleep(10)

    while not client.is_closed():
        print('on the loop')
        try:
        #if True:
            print('before checkupdates')
            await checkupdates(client, config)
            print('after checkupdates')
        except Exception as e:
            print(5, e)
            raise e
        #    pass
            # await logs.error(client, config, e)
        print('before sleep')
        await asyncio.sleep(10) # todo: pass this as a parameter
        print('after sleep')
    print('hooks are going down')
