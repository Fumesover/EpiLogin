import discord
import asyncio
import random
import string

import logs
import database
from database import BanType
import hooks

def hash_generator():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(64))

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
    try:
        url = config['website']['url'] + "/login/?next=/certify/?token=" + hash
        message = '\n'.join(config['bot']['welcome']) + '\n' + url

        await client.start_private_message(member)
        await client.send_message(member, message)

        return True
    except Exception:
        await logs.reject_mp(client, member, config)
        return False

async def check_not_confirmed(client, member, bdd, config):
    hash = await bdd.get_hash(member.id)
    if not hash:
        return False

    if await send_hello(client, member, hash, config):
        await logs.new_unconfirmed(client, member, hash, config)

    return True

async def new_user(client, member, bdd, config):
    if await check_not_confirmed(client, member, bdd, config):
        return

    hash = hash_generator()
    if await send_hello(client, member, hash, config):
        await bdd.add_user(member.id, hash)
        await logs.new_user(client, member, hash, config)

async def on_member_join(client, member, bdd, config):
    login = await bdd.get_login(member.id)

    if login == None:
        await new_user(client, member, bdd, config)
    else:
        ranks  = [] + config['servers'][member.server.id]['rank']
        groups = await bdd.get_groups(login)
        ranks += ids_of_roles(client, member.server, groups)

        if await check_ban(bdd, member.server.id, member.id, login, groups):
            ranks = [] + config['servers'][member.server.id]['banned']

        await give_roles(client, config, member, ranks)

    await hooks.push(config, {
        'joined': {'id':member.id, 'server':member.server.id, 'username': member.name}
    })

async def on_member_remove(Bot, member, bdd, config):
    await hooks.push(config, {
        'leaves': {'id':member.id, 'server':member.server.id}
    })

async def confirm_user(client, login, hash, config, bdd):
    id = await bdd.confirm_email(hash, login)
    print(id, login, hash)
    if not id:
        await logs.invalid_confirmation(client, login, hash, config)
        return

    await logs.confirm_login(client, login, hash, id, config)

    for server in client.servers:
        member = server.get_member(str(id))
        if member:
            ranks  = [] + config['servers'][member.server.id]['rank']
            groups = await bdd.get_groups(login)
            ranks += ids_of_roles(client, server, groups)

            if await check_ban(bdd, server.id, str(id), login, groups):
                ranks = [] + config['servers'][member.server.id]['banned']

            await give_roles(client, config, member, ranks)
            await logs.new_confirmed_user(client, member, login, config)

    await hooks.push(config, {
        'certify': {'id':str(id), 'login':login}
    })

async def check_ban(database, server_id, user_id, login, groups):
    if await database.check_ban(server_id, BanType.user, [user_id]):
        return True

    if await database.check_ban(server_id, BanType.login, [login]):
        return True

    if await database.check_ban(server_id, BanType.group, groups):
        return True

    return False
