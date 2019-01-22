import discord
import logging
import argparse
import yaml
import logging
import asyncio

import utils
import cri_fetch_promos
import database
from database import BanType
import logs

async def new_message(Bot, database, message, config):
    msg = message.content.split(' ')

    l = logging.getLogger('discord.admin')
    l.info(message.author.id + ' : ' + message.content)


    if msg[0] == 'help':
        msg = """```
EpiLogin: A bot to login with @epita.fr emails
- help                      <= show this message
- new *users                <= resend message for hash or add roles
- getlogin *users           <= get login of users
- picture *users            <= get face of users
- gethash *users            <= get hash of users
- getdiscord *logins        <= get discord account of logins
- delete *users             <= remove users from database
- fetchcri sessionID        <= update groups from CRI
- getgroups *logins         <= get groups from database
- addgroups login *groups   <= add groups to a login
- delgroups login *groups   <= del groups to a login
- certify user login        <= certify manualy a user
- ban [user|login|group] *data <= ban something from server
- unban [user|login|group] *data <= unban something from server
- isbanned [user|login|group] *data <= check if something is banned
- getbans                   <= get list of banned users
- find *groups              <= find users with all matching groups
```"""
        await Bot.send_message(message.channel, msg)
    elif msg[0] == 'new': # <= request hash or update roles
        for u in message.mentions:
            await Bot.on_member_join(u)
    elif msg[0] == 'getlogin':
        for u in message.mentions:
            login = await database.get_login(u.id)
            login = login if login else '**None**'
            await Bot.send_message(message.channel, u.mention + ' login is : ' + login)
    elif msg[0] == 'picture':
        for u in message.mentions:
            login = await database.get_login(u.id)
            login = login if login else '**None**'
            await Bot.send_message(message.channel, u.mention + ' : https://photos.cri.epita.fr/thumb/' + login)
    elif msg[0] == 'gethash':
        for u in message.mentions:
            hash = await database.get_hash(u.id)
            hash = hash if hash else '**None**'
            await Bot.send_message(message.channel, u.mention + ' hash is : ' + hash)
    elif msg[0] == 'getdiscord':
        for login in msg[1:]:
            ids = await database.get_ids(login)
            if ids == []:
                await Bot.send_message(message.channel, login + ' not found')
            else:
                for id in ids:
                    await Bot.send_message(message.channel, login + ' is <@' + str(id) + '>')
    elif msg[0] == 'delete':
        for u in message.mentions:
            await database.del_user(u.id)
            await Bot.send_message(message.channel, u.mention + ' deleted')
    elif msg[0] == 'fetchcri':
        l = logging.getLogger('discord.cri_fetch_promos')
        l.info(message.author.id + ' requested fetchcri')

        await cri_fetch_promos.cri_fetch_promos(database, msg[1], Bot, message.channel, config)
    elif msg[0] == 'getgroups':
        for login in msg[1:]:
            groups = await database.get_groups(login)
            await Bot.send_message(message.channel, login + ' : ' + ' '.join(groups))
    elif msg[0] == 'addgroups':
        login = msg[1]
        groups = msg[2:]
        await database.add_groups(login, groups)
        await Bot.send_message(message.channel, ' '.join(groups) + ' added to ' + login)
    elif msg[0] == 'delgroups':
        login = msg[1]
        groups = msg[2:]
        await database.del_groups(login, groups)
        await Bot.send_message(message.channel, ' '.join(groups) + ' removed to ' + login)
    elif msg[0] == 'logout':
        l = logging.getLogger('discord.admin.logout')
        l.info(message.author.id + ' requested shutdown')

        await database.close()

        config['email']['status'] = False
    elif msg[0] == 'certify':
        l = logging.getLogger('discord.admin.certify')
        l.info(message.author.id + ' certify that ' + msg[1] + ' is ' + msg[2])

        await utils.new_user(Bot, message.mentions[0], database, config)
        hash = await database.get_hash(message.mentions[0].id)

        await database.confirm_email(hash, msg[2])

        await utils.new_confirmed_user(Bot, message.mentions[0].id, msg[2], config, database)
    elif msg[0] == 'ban':
        server = message.server

        if msg[1] == 'user':
            for u in message.mentions:
                if not await database.check_ban(server.id, BanType.user, [u.id]):
                    await database.ban(server.id, BanType.user, u.id)
                    await logs.ban(Bot, config, server, BanType.user, [u.id])
        if msg[1] == 'login':
            for login in msg[2:]:
                if not await database.check_ban(server.id, BanType.login, [login]):
                    await database.ban(server.id, BanType.login, login)
                    await logs.ban(Bot, config, server, BanType.login, [login])
        if msg[1] == 'group':
            for group in msg[2:]:
                if not await database.check_ban(server.id, BanType.group, [group]):
                    await database.ban(server.id, BanType.group, group)
                    await logs.ban(Bot, config, server, BanType.group, [group])
    elif msg[0] == 'unban':
        server = message.server

        if msg[1] == 'user':
            for u in message.mentions:
                if await database.check_ban(server.id, BanType.user, [u.id]):
                    await database.unban(server.id, BanType.user, u.id)
                    await logs.unban(Bot, config, server, BanType.user, [u.id])
        if msg[1] == 'login':
            for login in msg[2:]:
                if await database.check_ban(server.id, BanType.login, [login]):
                    await database.unban(server.id, BanType.login, login)
                    await logs.unban(Bot, config, server, BanType.login, [login])
        if msg[1] == 'group':
            for group in msg[2:]:
                if await database.check_ban(server.id, BanType.group, [group]):
                    await database.unban(server.id, BanType.group, group)
                    await logs.unban(Bot, config, server, BanType.group, [group])
    elif msg[0] == 'isbanned':
        server = message.server

        if msg[1] == 'user':
            for u in message.mentions:
                if await database.check_ban(server.id, BanType.user, [u.id]):
                    await Bot.send_message(message.channel, u.mention + ' is banned')
                else:
                    await Bot.send_message(message.channel, u.mention + ' isn\'t banned')
        if msg[1] == 'login':
            for login in msg[2:]:
                if await database.check_ban(server.id, BanType.login, [login]):
                    await Bot.send_message(message.channel, login + ' is banned')
                else:
                    await Bot.send_message(message.channel, login + ' isn\'t banned')
        if msg[1] == 'group':
            for group in msg[2:]:
                if await database.check_ban(server.id, BanType.group, [group]):
                    await Bot.send_message(message.channel, group + ' is banned')
                else:
                    await Bot.send_message(message.channel, group + ' isn\'t banned')
    elif msg[0] == 'getbans':
        data = await database.get_bans(message.server.id)
        for d in data:
            type = BanType(d['type'])
            if type == BanType.login:
                await Bot.send_message(message.channel, 'login : ' + d['value'] + ' is banned')
            if type == BanType.user:
                await Bot.send_message(message.channel, 'user : <@' + d['value'] + '> is banned')
            if type == BanType.group:
                await Bot.send_message(message.channel, 'group : ' + d['value'] + ' is banned')
    elif msg[0] == 'find':
        groups = msg[1:]
        to_ping = []

        for member in message.server.members:
            login = await database.get_login(member.id)
            if login:
                ugroups = await database.get_groups(login)
                if all([g in ugroups for g in groups]):
                    to_ping.append(member.mention)

        msg = ""
        for mention in to_ping:
            if len(msg + mention) > 2000:
                await Bot.send_message(message.channel, msg)
                msg = ''
            else:
                msg += mention
        if msg:
            await Bot.send_message(message.channel, msg)
