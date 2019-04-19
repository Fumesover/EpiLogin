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
    if not (added or removed):
        message = " no roles to set"

    l = get_logger('discord.epilogin.set_roles')
    l.info(str(member.id) + message)

    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send(member.mention + message)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : ' + member.mention + message)

async def reject_dm(client, member, config):
    msg = "{} does not accept DM"

    l = get_logger('discord.epilogin.reject_dm')
    l.info(str(member.guild.id) + ':' + msg.format(member.id))

    channel = get_channel(client, config['servers'][member.guild.id]['channel_logs'])
    await channel.send(msg.format(member.mention))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(member.guild.name + ' : ' + msg.format(member.mention))

async def on_guild_join(client, config, guild):
    msg = "I just joinded {} ! You need to activate it on {}/servers/{}".format(guild.name, config['website']['url'], guild.id)

    l = get_logger('discord.epilogin.on_guild_join')
    l.info(msg)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(msg)

async def on_guild_activate(client, config, guild_id, author):
    guild = client.get_guild(guild_id)
    msg = "<@{}> just activated {} ({}).".format(author, guild.name, guild_id)

    l = get_logger('discord.epilogin.on_guild_activate')
    l.info(msg)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(msg)

async def on_guild_deactivate(client, config, guild_id, author):
    guild = client.get_guild(guild_id)
    msg = "<@{}> just deactivate {} ({}).".format(author, guild.name, guild_id)

    l = get_logger('discord.epilogin.on_guild_deactivate')
    l.info(msg)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(msg)

async def on_add_domain(client, config, guild_id, author, domain):
    guild = client.get_guild(guild_id)
    msg = "<@{}> just added @{} to whitelist.".format(author, domain)

    l = get_logger('discord.epilogin.on_add_domain')
    l.info("{}: {}".format(guild.id, msg))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send("{}: {}".format(guild.name, msg))

    channel = get_channel(client, config['servers'][guild_id]['channel_logs'])
    await channel.send(msg)

async def on_del_domain(client, config, guild_id, author, domain):
    guild = client.get_guild(guild_id)
    msg = "<@{}> just removed @{} from whitelist.".format(author, domain)

    l = get_logger('discord.epilogin.on_del_domain')
    l.info("{}: {}".format(guild.id, msg))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send("{}: {}".format(guild.name, msg))

    channel = get_channel(client, config['servers'][guild_id]['channel_logs'])
    await channel.send(msg)

async def on_channels_update(client, config, guild_id, author):
    guild = client.get_guild(guild_id)
    conf = config['servers'][guild_id]
    msg = (
            "<@{}> updated the configuration:\n"
            "\tLogs: <#{}>\n"
            "\tAdmin: <#{}>\n"
            "\tRequest: <#{}>"
          ).format(author, conf['channel_logs'], conf['channel_admin'], conf['channel_request'])

    l = get_logger('discord.epilogin.on_del_domain')
    l.info("{}: {}".format(guild.id, msg))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send("{}: {}".format(guild.name, msg))

    channel = get_channel(client, config['servers'][guild_id]['channel_logs'])
    await channel.send(msg)

async def on_update_rank(client, config, guild_id, author, msg):
    guild = client.get_guild(guild_id)
    msg = "<@{}> {}".format(author, msg)

    l = get_logger('discord.epilogin.on_update_rank')
    l.info("{}: {}".format(guild.id, msg))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send("{}: {}".format(guild.name, msg))

    channel = get_channel(client, config['servers'][guild_id]['channel_logs'])
    await channel.send(msg)

async def certify(client, config, user_id, email, author):
    msg = "<@{}> manualy certified that <@{}> is {}".format(author, user_id, email)

    l = get_logger('discord.epilogin.certify')
    l.info(msg)

    channel = get_channel(client, config['bot']['logs'])
    await channel.send(msg)

async def ban(client, config, author, guild, type, victim, unban=False):
    msg = "<@{}> {}banned {} {}".format(author, 'un' if unban else '', type, victim if type != 'user' else '<@{}>'.format(victim))

    l = get_logger('discord.epilogin.ban')
    l.info("{}: {}".format(guild.id, msg))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send("{}: {}".format(guild.name, msg))

    channel = get_channel(client, config['servers'][guild.id]['channel_logs'])
    await channel.send(msg)

async def error(client, config, e):
    l = get_logger('discord.error')
    l.info('error: ' + str(e))

    channel = get_channel(client, config['bot']['logs'])
    await channel.send('error: ' + str(e))
