#!/bin/python

import asyncio
import discord
import logging
import argparse
import yaml
import time

import utils
import admin
import hooks
import api

logging.basicConfig(level=logging.INFO)

Bot    = discord.Client()
config = None

@Bot.event
async def on_ready():
    for guild in Bot.guilds:
        api.on_guild_join(config, guild.id)
    api.update_conf_all(config)

@Bot.event
async def on_message(message):
    if message.author == Bot.user:
        return
    if message.guild == None:
        return

    guild_id = message.guild.id

    if (not guild_id in config['servers']) or not config['servers'][guild_id]['is_active']:
        return

    if message.channel.id == config['servers'][guild_id]['channel_admin']:
        await admin.new_message(Bot, message, config)
    if message.channel.id == config['servers'][guild_id]['channel_request']:
        await utils.on_member_join(Bot, message.author, config)

@Bot.event
async def on_member_join(member):
    await utils.on_member_join(Bot, member, config)

@Bot.event
async def on_member_remove(member):
    api.on_member_remove(config, member.id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Discord bot for EPITA')
    parser.add_argument('-c', '--config', default='config.yml', help='config file, default is config.yml')
    args = parser.parse_args()

    with open(args.config, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    Bot.loop.create_task(
        hooks.hooksthread(Bot, config)
    )

    Bot.run(config['bot']['tokken'])
