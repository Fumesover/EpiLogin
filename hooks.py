import discord
import asyncio
import logging
import json
import requests

import utils

def checkupdates(client, config, database):
#    l = logs.get_logger('hooks.checkupdates')
#    l.info('checking updates ...')

    data = api.get_updates()
    confirmed = []

    def confirmed(data):
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
        'CONFIRMED': confirmed,
        'BAN': ban,
        'UNBAN': unban,
        'DELGROUP': addgroup,
        'ADDGROUP': delgroup
    }

    for update in data:
        pass

    if confirmed:
        r = api.del_updates(confirmed)

async def hooksthread(client, config):
    while not client.is_closed:
        try:
            await checkupdates(client, config)
        except Exception as e:
            pass
            # await logs.error(client, config, e)

        await asyncio.sleep(60) # todo: pass this as a parameter
