import discord
import asyncio
import logging
import json
import requests

import utils
import api
import logs

async def checkupdates(client, config):
    data = api.get_updates(config)
    confirmed = []

    async def certify(data):
        user_id    = int(data['value'])
        user_email = data['email']

        for guild in client.guilds:
            m = guild.get_member(user_id)
            if m:
                await utils.on_certify(client, config, m, user_email)
        confirmed.append(data['id'])

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
                await utils.set_roles(client, config, m, to_set)

        async def ban_email(data):
            ids = api.get_ids(config, data['email'])
            for id in ids:
                if 'id' in id:
                    await ban_user({'value': str(id['id'])})

        async def ban_group(data):
            users = api.get_groups(config, group=data['value'])
            for user in users:
                await ban_email(user)

        handler = {
            'user': ban_user,
            'group': ban_group,
            'email': ban_email,
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

        async def unban_email(data):
            ids = api.get_ids(config, data['email'])
            for id in ids:
                if 'id' in id:
                    await unban_user({'value': str(id['id'])})

        async def unban_group(data):
            users = api.get_groups(config, group=data['value'])
            for user in users:
                await unban_email(user)

        handler = {
            'user': unban_user,
            'group': unban_group,
            'email': unban_email,
        }

        if data['ban_type'] in handler:
            await handler[data['ban_type']](data)

        confirmed.append(data['id'])

    async def addgroup(data):
        email = data['email']
        ids = api.get_ids(config, email)

        for user in ids:
            if not user['id']:
                continue

            for guild in client.guilds:
                config_ranks = config['servers'][guild.id]['ranks']
                if data['value'] in config_ranks['classic']:
                    role = config_ranks['classic'][data['value']]

                    m = guild.get_member(user['id'])
                    if m:
                        roles = await utils.__add_roles(m, role)
                        await logs.set_roles(client, config, m, roles, [])

        confirmed.append(data['id'])

    async def delgroup(data):
        email = data['email']
        ids = api.get_ids(config, email)

        for user in ids:
            if not user['id']:
                continue

            for guild in client.guilds:
                config_ranks = config['servers'][guild.id]['ranks']
                if data['value'] in config_ranks['classic']:
                    role = config_ranks['classic'][data['value']]

                    m = guild.get_member(user['id'])
                    if m:
                        roles = await utils.__del_roles(m, role)
                        await logs.set_roles(client, config, m, [], roles)
        confirmed.append(data['id'])

    async def updateconfig(data):
        guild_id = data['server']
        await api.update_conf(client, config, guild_id)
        confirmed.append(data['id'])

    handelers = {
        'certify': certify,
        'ban': ban,
        'unban': unban,
        'addgroup': addgroup,
        'delgroup': delgroup,
        'config': updateconfig,
    }

    for update in data:
        if 'type' in update and update['type'] in handelers:
            await handelers[update['type']](update)

    if confirmed:
        r = api.del_updates(config, confirmed)

async def hooksthread(client, config):
    await client.wait_until_ready()

    while not 'servers' in config:
        await asyncio.sleep(10)

    while not client.is_closed():
        try:
            await checkupdates(client, config)
        except Exception as e:
            print(e)
            # raise e

        await asyncio.sleep(10) # todo: pass this as a parameter
