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

    print(config)

    async def certify(data):
        #{
        #    'id': 2,
        #    'type': 'certify',
        #    'ban_type': '',
        #    'login': 'albin.parou',
        #    'value': '238378747357560832',
        #    'server': None
        #}

        user_id    = int(data['value'])
        user_login = data['login']

        print(user_login)

        for guild in client.guilds:
            m = guild.get_member(user_id)
            if m:
                print(42)
                await utils.on_certify(config, m, user_login)
                print(890)
        confirmed.append(data['id'])

    async def ban(data):
        pass

    async def unban(data):
        pass

    async def addgroup(data):
        pass

    async def delgroup(data):
        pass

    handelers = {
        'certify': certify,
        'ban': ban,
        'unban': unban,
        'addgroup': delgroup,
        'delgroup': addgroup,
    }

    for update in data:
        if 'type' in update and update['type'] in handelers:
            await handelers[update['type']](update)
        else:
            print('wtf ?', update)
        # print(update)


    print(confirmed)

    if confirmed:
        r = api.del_updates(config, confirmed)

async def hooksthread(client, config):
    await client.wait_until_ready()
    await asyncio.sleep(10)

    while not client.is_closed():
        print(2)
        #try:
        if True:
            print(3)
            await checkupdates(client, config)
            print(4)
        #except Exception as e:
        #    print(5, e)
        #    pass
            # await logs.error(client, config, e)
        print(6)
        await asyncio.sleep(60) # todo: pass this as a parameter
        print(7)
    print(8)
