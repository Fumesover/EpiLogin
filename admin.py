import discord
import logging
import argparse
import yaml
import database
import logging
import asyncio

import utils
import cri_fetch_promos

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
