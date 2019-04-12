import discord
import asyncio
import logging

def get_logger(name):
    return logging.getLogger(name)

def get_channel(client, id):
    return client.get_channel(id)

async def on_ready(client, config):
    l = get_logger('discord.epilogin.on_ready')
    l.info('logged in as ' + client.user.name)
    for guild in client.guilds:
        l.info('connected to ' + guild.name + ' (' + str(guild.id) + ')')

    channel = get_channel(client, config['bot']['logs'])
    await channel.send('Client ready')

async def config_loaded(client, config):
    l = get_logger('discord.epilogin.config_loaded')
    l.info('Config loaded')

    channel = get_channel(client, config['bot']['logs'])
    await channel.send('Config loaded')

async def admin_command(client, config, message):
    l = get_logger('discord.epilogin.admin_command')
    l.info(str(message.author.id) + ' : ' + message.content)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(message.guild.name + " | " + str(message.author) + ' : ' + message.content)

async def config_updated(client, config, guild):
    l = get_logger('discord.epilogin.config_loaded')
    l.info('Config updated for ' + str(guild.id))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send('Config updated for ' + guild.name)

    channel = get_channel(client, config['servers'][guild.id]['channel_logs'])
    await channel.send('Config updated for ' + guild.name)

async def new_user(client, member, config):
    l = get_logger('discord.epilogin.new_user')
    l.info(str(member.id) + ' arrived on ' + str(member.guild.id))

    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send('New user (waiting for confirmation) : ' + member.mention)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : new user (waiting for confirmation) : ' + member.mention)

async def set_roles(client, config, member, added, removed):
    n_added   = ' '.join([r.name for r in added])
    n_removed = ' '.join([r.name for r in removed])

    message = ''
    if added:
        message += " adding {}".format(n_added)
        if removed:
            message += " and"
    if removed:
        message += " removing {}".format(n_removed)
    if not added and not removed:
        message = " no roles to set"

    l = get_logger('discord.epilogin.set_roles')
    l.info(str(member.id) + message)

    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send(member.mention + message)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : ' + member.mention + message)

async def reject_dm(client, member, config):
    msg = "{} does not accept DM" #.format(member.mention)

    l = get_logger('discord.epilogin.reject_dm')
    l.info(str(member.guild.id) + ':' + msg.format(member.id))

    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send(msg.format(member.mention))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : ' + msg.format(member.mention))
