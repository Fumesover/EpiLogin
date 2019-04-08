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
    l = get_logger('discord.epilogin.set_roles')
    l.info(str(member.id) + ' adding ' + str(added) + ' & removing' + str(removed))

    n_added   = ' '.join([r.name for r in added])
    m_added   = ' '.join([r.mention for r in added])
    n_removed = ' '.join([r.name for r in removed])
    m_removed = ' '.join([r.mention for r in removed])
    
    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send(member.mention + ' adding [' + m_added + '] and removing [' + m_removed + ']')

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : ' + member.mention + ' adding [' + n_added + '] and removing [' + n_removed + ']')
