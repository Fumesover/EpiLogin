import discord
import asyncio
import string

import api

async def del_roles(client, config, member, roles):
    if member and client and roles:
        server = member.guild
        to_remove = []
        for role in roles:
            r = discord.utils.get(server.roles, id=role)
            if r: to_remove.append(r)

        await client.remove_roles(member, *to_remove)

async def give_roles(client, config, member, roles, id=True):
    if member and client and roles:
        server = member.guild
        new_roles = []
        for role in roles:
            r = discord.utils.get(server.roles, id=role)
            if r: new_roles.append(r)

        await client.add_roles(member, *new_roles)

async def send_hello(client, member, hash, config):
    try:
        url = config['website']['url'] + "/login/?next=/certify/?token=" + hash
        message = '\n'.join([
            string.Template(s).safe_substitute(
                server=member.guild.name,
            ) for s in config['bot']['welcome']
        ]) + '\n' + url

        await client.start_private_message(member)
        await client.send_message(member, message)

    except Exception:
        pass

async def on_member_join(client, member, config, create_if_unk=True):
    user = api.get_member(member.id)
    api.on_member_join(member.guild.id, member.id)

    if not user:
        if create_if_unk:
            user = api.create_member(member.id)
        else:
            return

    login = user['login']

    if not login:
        send_hello(client, member, user['hash'], config)
    else:
        config_ranks = config['servers'][member.guild.id]['ranks']

        user_groups = api.get_groups(login)
        user_groups = user_groups if user_groups else []

        ranks = [id for id in user_groups if id in config_ranks['classic']]

        if check_ban(member, login, ranks, config):
            ranks = config_ranks['banned']
        else:
            ranks += config_ranks['confirmed']

        await give_roles(client, config, member, ranks)

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
