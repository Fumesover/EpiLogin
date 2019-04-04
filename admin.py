import discord
import asyncio
import re

import utils
import api

__re_id_form_tag = re.compile('([0-9]{18})')

async def new_message(Bot, database, message, config):
    msg = message.content.split(' ')

    async def help():
        msg = """```
    Usage:
    - help                            show this message
    - new    [*users | @everyone]     send hello message or update
    - update [*users | @everyone]     update roles of user
    - this                            get the server page on website
    - get    [*users | id | login]    get the member page on website
    - logout                          shut down the bot
    - syncconf [this | all]           reload configuration from server
    ```"""
        await Bot.send_message(message.channel, msg)

    async def update(create_if_unk=False):
        if message.mention_everyone:
            for u in message.guild.members:
                await Bot.on_member_join(Bot, u, config, create_if_unk=create_if_unk)
        else:
            for u in message.mentions:
                await Bot.on_member_join(Bot, u, config, create_if_unk=create_if_unk)

    async def new():
        await update(create_if_unk=True)

    async def this():
        msg = "{}/servers/{}/".format(config['website']['url'], message.guild.id)
        await Bot.send_message(message.channel, msg)

    async def get():
        ids = []

        for el in msg[1:]:
            req = __re_id_form_tag.match(el)
            if req:
                ids.append((True, el, req.match(1)))
            else:
                ids = api.get_ids(el)
                for id in ids:
                    ids.append((True, el, id))
                if not ids:
                    ids.append((False, el, el))

        for (found, el, id) in ids:
            if found:
                msg = '{} not found'.format(el)
            else:
                msg = '{} found: {}/members/{}/'.format(el, config['website']['url'], id)
            await Bot.send_message(message.channel, msg)

    async def syncconf():
        if len(msg) < 2:
            return
        elif msg[1] == 'all':
            api.update_conf_all()
        elif msg[1] == 'this':
            api.update_conf(message.guild.id)

    async def logout():
        await Bot.logout()

    handler = {
        'help': help,
        'update': update,
        'new': new,
        'this': this,
        'get': get,
        'syncconf': syncconf,
        'logout': logout,
    }

    if msg[0] in handler:
        handler[msg[0]]()
