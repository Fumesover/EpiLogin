import discord
import asyncio
import random
import string

import logs
import database

def hash_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

def ids_of_roles(client, server, roles):
    output = []

    if client and roles and server:
        for role in roles:
            r = discord.utils.get(server.roles, name=role)
            if r: output.append(r.id)

    return output

async def del_roles(client, config, member, roles):
    if member and client and roles:
        server = member.server
        to_remove = []
        for role in roles:
            r = discord.utils.get(server.roles, name=role)
            if r: to_remove.append(r)

        await client.remove_roles(member, *to_remove)
        await logs.del_roles(client, config, member, to_remove)

async def give_roles(client, config, member, roles, id=True):
    if member and client and roles:
        server = member.server
        new_roles = []
        for role in roles:
            r = discord.utils.get(server.roles, id=role)
            if r: new_roles.append(r)

        await client.add_roles(member, *new_roles)
        await logs.new_roles(client, config, member, new_roles)

async def send_hello(client, member, hash, config):
    await client.start_private_message(member)
    await client.send_message(member, '\n'.join(config['bot']['welcome']))
    await client.send_message(member, "[" + hash +"]")

async def check_not_confirmed(client, member, bdd, config):
    hash = await bdd.get_hash(member.id)
    if not hash:
        return False

    await send_hello(client, member, hash, config)
    await logs.new_unconfirmed(client, member, hash, config)

    return True

async def new_user(client, member, bdd, config):
    if await check_not_confirmed(client, member, bdd, config):
        return

    hash = hash_generator()
    await send_hello(client, member, hash, config)

    await bdd.add_user(member.id, hash)
    await logs.new_user(client, member, hash, config)

async def on_member_join(client, member, bdd, config):
    login = await bdd.get_login(member.id)

    if login == None:
        await new_user(client, member, bdd, config)
    else:
        ranks = [] + config['servers'][member.server.id]['rank']
        groups = await bdd.get_groups(login)
        ranks += ids_of_roles(client, member.server, groups)

        await give_roles(client, config, member, ranks)

async def new_confirmed_user(client, id, login, config, bdd):
    for server in client.servers:
        member = server.get_member(str(id))
        if member:
            ranks = [] + config['servers'][member.server.id]['rank']
            ranks += ids_of_roles(client, server, await bdd.get_groups(login))

            await give_roles(client, config, member, ranks)
