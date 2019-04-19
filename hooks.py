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

        if data['author'] != user_id:
            await logs.certify(client, config, user_id, user_email, data['author'])

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
            await logs.ban(client, config, data['author'], guild, data['ban_type'], data['value'])

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
            await logs.ban(client, config, data['author'], guild, data['ban_type'], data['value'], unban=True)

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
        value = data['value'].split('-')

        async def channels_update(data):
            await api.update_conf(client, config, data['server'])
            await logs.on_channels_update(client, config, data['server'], data['author'])
        async def deldomain(data):
            config['servers'][data['server']]['domains'].remove(data['email'])
            await logs.on_del_domain(client, config, data['server'], data['author'], data['email'])
        async def adddomain(data):
            config['servers'][data['server']]['domains'].append(data['ban_type'])
            await logs.on_add_domain(client, config, data['server'], data['author'], data['ban_type'])
        async def activate(data):
            config['servers'][data['server']]['is_active'] = True
            await logs.on_guild_activate(client, config, data['server'], data['author'])
        async def deactivate(data):
            config['servers'][data['server']]['is_active'] = False
            await logs.on_guild_deactivate(client, config, data['server'], data['author'])
        async def delrank(data):
            async def delconfirmed():
                config['servers'][data['server']]['ranks']['confirmed'].remove(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "removed <@&{}> for confirmed".format(int(data['email']))
                )
            async def delbanned():
                config['servers'][data['server']]['ranks']['banned'].remove(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "removed <@&{}> for banned".format(int(data['email']))
                )
            async def delclassic():
                config['servers'][data['server']]['ranks']['classic'][data['ban_type']].remove(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "removed <@&{}> for {}".format(int(data['email']), data['ban_type'])
                )

            handelers = {
                'confirmed': delconfirmed,
                'banned': delbanned,
                'classic': delclassic,
            }

            if value[1] in handelers:
                await handelers[value[1]]()
                confirmed.append(data['id'])
        async def addrank(data):
            async def addconfirmed():
                config['servers'][data['server']]['ranks']['confirmed'].append(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "added <@&{}> for confirmed".format(int(data['email']))
                )
            async def addbanned():
                config['servers'][data['server']]['ranks']['banned'].append(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "added <@&{}> for banned".format(int(data['email']))
                )
            async def addclassic():
                if not data['ban_type'] in config['servers'][data['server']]['ranks']['classic']:
                    config['servers'][data['server']]['ranks']['classic'][data['ban_type']] = []
                config['servers'][data['server']]['ranks']['classic'][data['ban_type']].append(int(data['email']))
                await logs.on_update_rank(
                        client, config, data['server'], data['author'],
                        "added <@&{}> for {}".format(int(data['email']), data['ban_type'])
                )

            handelers = {
                'confirmed': addconfirmed,
                'banned': addbanned,
                'classic': addclassic,
            }

            if value[1] in handelers:
                await handelers[value[1]]()
                confirmed.append(data['id'])

        handelers = {
            'channels': channels_update,
            'deldomain': deldomain,
            'adddomain': adddomain,
            'activate': activate,
            'deactivate': deactivate,
            'addrank': addrank,
            'delrank': delrank
        }

        if value[0] in handelers:
            await handelers[value[0]](data)
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

        await asyncio.sleep(config['website']['time'])
