import discord
import asyncio
import re

import utils
import api

__re_id_form_tag = re.compile('([0-9]{18})')

async def new_message(Bot, message, config):
    msg = message.content.split(' ')

    async def help():
        msg = (
            "```Usage:\n"
            "- help                            show this message\n"
            "- new    [*users | @everyone]     send hello message or update\n"
            "- update [*users | @everyone]     update roles of user\n"
            "- get    [*users | id | login]    get the member page on website\n"
            "- this                            get the server page on website\n"
            "- logout                          shut down the bot\n"
            "- syncconf [this | all]           reload configuration from server```"
        )
        await message.channel.send(msg)

    async def update(create_if_unk=False):
        if message.mention_everyone:
            for u in message.guild.members:
                await utils.on_member_join(Bot, u, config, create_if_unk=create_if_unk)
        else:
            for u in message.mentions:
                await utils.on_member_join(Bot, u, config, create_if_unk=create_if_unk)

    async def new():
        await update(create_if_unk=True)

    async def this():
        msg = "{}/servers/{}/".format(config['website']['url'], message.guild.id)
        await message.channel.send(msg)

    async def get():
        ids = []

        for el in msg[1:]:
            req = __re_id_form_tag.match(el)
            if req:
                ids.append((True, el, req.match(1)))
            else:
                ids = api.get_ids(config, el)
                for id in ids:
                    ids.append((True, el, id))
                if not ids:
                    ids.append((False, el, el))

        for (found, el, id) in ids:
            if found:
                msg = '{} not found'.format(el)
            else:
                msg = '{} found: {}/members/{}/'.format(el, config['website']['url'], id)
            await message.channel.send(msg)

    async def syncconf():
        if len(msg) < 2:
            return
        elif msg[1] == 'all':
            api.update_conf_all(config)
        elif msg[1] == 'this':
            api.update_conf(config, message.guild.id)

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
        await handler[msg[0]]()
