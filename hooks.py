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

    def certify(data):
        {
            'id': 2,
            'type': 'certify',
            'ban_type': '',
            'login': 'albin.parou',
            'value': '238378747357560832',
            'server': None
        }

        pass

    def ban(data):
        pass

    def unban(data):
        pass

    def addgroup(data):
        pass

    def delgroup(data):
        pass

    handelers = {
        'certify': certify,
        'ban': ban,
        'unban': unban,
        'addgroup': delgroup,
        'delgroup': addgroup,
    }

    for update in data:
        print(update)

    print(confirmed)

    if confirmed:
        r = api.del_updates(confirmed)

async def hooksthread(client, config):
    await client.wait_until_ready()
    while not client.is_closed():
        print(2)
        try:
            print(3)
            await checkupdates(client, config)
            print(4)
        except Exception as e:
            print(5, e)
            pass
            # await logs.error(client, config, e)
        print(6)
        await asyncio.sleep(60) # todo: pass this as a parameter
        print(7)
    print(8)
