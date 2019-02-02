#!/bin/python3.6

import asyncio
import discord
import logging
import argparse
import yaml

import utils
import admin
import database
import logs
import hooks

logging.basicConfig(level=logging.INFO)

Bot    = discord.Client()
config = None
bdd    = None

@Bot.event
async def on_ready():
    await logs.on_ready(Bot, config)

@Bot.event # Admin zone
async def on_message(message):
    if message.author == Bot.user:
        return # Avoid loops
    if message.server == None:
        return # No MP

    if message.channel.id == config['servers'][message.server.id]['admin']:
        await admin.new_message(Bot, bdd, message, config)
    if message.channel.id == config['servers'][message.server.id]['request']:
        await utils.on_member_join(Bot, message.author, bdd, config)

@Bot.event
async def on_member_join(member):
    await utils.on_member_join(Bot, member, bdd, config)

@Bot.event
async def on_member_remove(member):
    await utils.on_member_remove(Bot, member, bdd, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord bot for EPITA')
    parser.add_argument('-c', '--config', default='config.yml', help='config file, default is config.yml')
    args = parser.parse_args()

    configfile = args.config
    with open(configfile, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    # Load config & databases
    bdd = database.database() # Init DB here
    asyncio.get_event_loop().run_until_complete(bdd.init(config))

    # Add webhooks process
    if config['website']['enable']:
        Bot.loop.create_task(
            hooks.hooksthread(Bot, config, bdd)
        )

    Bot.run(config['bot']['tokken'])
