import discord
import asyncio
import string

import api

async def del_roles(member, roles):
    if member and roles:
        server = member.guild
        to_remove = []
        for role in roles:
            r = member.guild.get_role(role)
            if r:
                to_remove.append(r)

# TODO: handle errors (cf https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Member.add_roles)
        await member.remove_roles(*to_remove)

async def give_roles(member, roles):
    if member and roles:
        server = member.guild
        new_roles = []
        for role in roles:
            r = member.guild.get_role(role)
            if r:
                new_roles.append(r)

# TODO: handle errors (cf https://discordpy.readthedocs.io/en/rewrite/api.html#discord.Member.add_roles)
        await member.add_roles(*new_roles)

async def set_roles(config, member, to_set):
    conf_roles = config['servers'][member.guild.id]['ranks']

    to_del = [] + conf_roles['banned'] + conf_roles['confirmed']
    for role in conf_roles['classic']:
        to_del += conf_roles['classic'][role]

    for role in to_set:
        if role in to_del:
            to_del.remove(role)

    user_roles = [r.id for r in member.roles]

    to_remove = [id for id in to_del if id in user_roles]
    to_add    = [id for id in to_set if not id in user_roles]

    await del_roles(member, to_remove)
    await add_roles(member, to_add)

async def send_hello(client, member, hash, config):
    try:
        url = config['website']['url'] + "/login/?next=/certify/?token=" + hash
        message = '\n'.join([
            string.Template(s).safe_substitute(
                server=member.guild.name,
            ) for s in config['bot']['welcome']
        ]) + '\n' + url

        channel = member.dm_channel
        if not channel:
            channel = await member.create_dm()

        await channel.send(message)

    except Exception:
        print('TODO: send_hello: add logs here')
        pass

async def on_member_join(client, member, config, create_if_unk=True):
    user = api.get_member(config, member.id)
    api.on_member_join(config, member.guild.id, member.id)

    if not user:
        if not create_if_unk:
            return
        user = api.create_member(config, member.id)

    login = user['login']

    if not login:
        await send_hello(client, member, user['hash'], config)
    else:
        config_ranks = config['servers'][member.guild.id]['ranks']

        user_groups = api.get_groups(config, login)
        user_groups = user_groups if user_groups else []

        ranks = []
        for group in user_groups:
            if group['group'] in config_ranks['classic']:
                ranks += config_ranks['classic'][group['group']]

        if check_ban(member, login, ranks, config):
            ranks = config_ranks['banned']
        else:
            ranks += config_ranks['confirmed']

        # await give_roles(client, config, member, ranks)
        await set_roles(config, member, ranks)

def check_ban(member, login, groups, config):
    server_id = member.guild.id

    if login in config['servers'][server_id]['bans']['login']:
        return True

    if member.id in config['servers'][server_id]['bans']['user']:
        return True

    for group in groups:
        if group in config['servers'][server_id]['bans']['group']:
            return True

    return False
