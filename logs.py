import discord
import logging
from database import BanType

def get_logger(name):
    return logging.getLogger(name)

def get_channel(client, id):
    return discord.utils.get(client.get_all_channels(), id=id)

async def on_ready(client, config):
    l = get_logger('discord.epilogin.on_ready')
    l.info('logged in as ' + client.user.name)
    for server in client.servers:
        l.info('connected to ' + server.name + ' (' + server.id + ')')

async def new_user(client, member, hash, config):
    l = get_logger('discord.epilogin.new_user')
    l.info(member.id + ' arrived on ' + member.server.id + ' hash is [' + hash + ']')

    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' is unknown and recived a mp')

async def new_unconfirmed(client, member, hash, config):
    l = get_logger('discord.epilogin.new_unconfirmed')
    l.info(member.id + ' arrived on ' + member.server.id + ' hash is [' + hash + ']')

    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' never confirmed and recived a new mp')

async def new_roles(client, config, member, list):
    roles = ' '.join([r.mention for r in list])

    l = get_logger('discord.epilogin.new_roles')
    l.info(member.id + ' just got on ' + member.server.id + ' ' + roles)

    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' just got ' + roles)

async def del_roles(client, config, member, list):
    roles = ' '.join([r.mention for r in list])

    l = get_logger('discord.epilogin.del_roles')
    l.info(member.id + ' just got removed on ' + member.server.id + ' ' + roles)

    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' just got ' + roles)

async def email_unknown_hash(hash, login):
    l = get_logger('discord.epilogin.email_unknown_hash')
    l.info('mail by ' + login + ' unknown hash : ' + hash)

async def email_confimed(client, login, hash, id):
    l = get_logger('discord.epilogin.email_confimed')
    l.info(str(id) + ' confirmed to be ' + login + ' with hash : ' + hash)

async def invalid_email(client, sender, subject):
    l = get_logger('discord.epilogin.invalid_email')
    l.info('invalid email : from <' + sender + '> subject <' + subject + '>')

async def database_del_groups(login, groups):
    l = get_logger('database.del_groups')
    l.info(login + ' removing groups ' + str(groups))

async def database_add_groups(login, groups):
    l = get_logger('database.add_groups')
    l.info(login + ' adding groups ' + str(groups))

async def new_confirmed_user(client, member, login, config):
    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' is ' + login)

async def reject_mp(client, member, config):
    l = get_logger('discord.new_user.reject_mp')
    l.info(member.id + ' reject epilogin\'s mp')

    channel = get_channel(client, config['servers'][member.server.id]['logs'])
    await client.send_message(channel, member.mention + ' does not accept mp')

async def ban(client, config, server, type, data):
    if type == BanType.user:
        data = ['<@' + d + '>' for d in data]

    l = get_logger('discord.admin.ban')
    l.info('banning ' + ' '.join(data) + ' from ' + server.id)

    channel = get_channel(client, config['servers'][server.id]['logs'])
    await client.send_message(channel, 'banning ' + ' '.join(data))

async def unban(client, config, server, type, data):
    if type == BanType.user:
        data = ['<@' + d + '>' for d in data]

    l = get_logger('discord.admin.unban')
    l.info('unbanning ' + ' '.join(data) + ' from ' + server.id)

    channel = get_channel(client, config['servers'][server.id]['logs'])
    await client.send_message(channel, 'unbanning ' + ' '.join(data))
