#!/bin/python3.6

import asyncio
import discord
import logging
import argparse
import yaml

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
        api.on_guild_join(guild.id)
    api.__update_conf_all()

@Bot.event
async def on_message(message):
    if message.author == Bot.user:
        return
    if message.guild == None:
        return

    if message.channel.id == config['servers'][message.guild.id]['channel_admin']:
        await admin.new_message(Bot, message, config)
    if message.channel.id == config['servers'][message.guild.id]['channel_request']:
        await utils.on_member_join(Bot, message.author, config)

@Bot.event
async def on_member_join(member):
    await utils.on_member_join(Bot, member, config)

@Bot.event
async def on_member_remove(member):
    api.on_member_remove(member.id)

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
