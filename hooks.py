import discord
import asyncio
import logging
import json
import requests

import utils
import logs

def checkupdates(client, config, database):
    l = logs.get_logger('hooks.checkupdates')
    l.info('checking updates ...')

    data = api.get_updates()
    confirmed = []

    if False:
        trucs = [
            'CONFIRMED',
            'BAN',
            'UNBAN',
            'DELGROUP',
            'ADDGROUP'
        ]

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
            await logs.error(client, config, e)

        await asyncio.sleep(60) # todo: pass this as a parameter
