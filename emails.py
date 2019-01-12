import discord
import email
import re
import asyncio
from   imaplib import IMAP4
import discord
import logging

import database
import utils
import logs

regexlogin = '^.* <([a-zA-Z0-9_.+-]+)@(?:(?:[a-zA-Z0-9-]+\\.)?[a-zA-Z]+\\.)?epita\\.fr>'
regexhash  = '^\[([A-Z0-9]*)]'

async def mailthread(client, config, database):
    client.wait_until_ready()

    imap = IMAP4(config['email']['url'])
    if config['email']['usetls']:
        imap.starttls()
    imap.login(config['email']['login'], config['email']['password'])

    while config['email']['status'] and not client.is_closed:
        imap.select(config['email']['inbox'])
        _, data = imap.search(None, 'ALL')

        if data[0] == b'':
            await asyncio.sleep(30)
        else:
            for num in data[0].split():
                e    = imap.fetch(num, '(RFC822)')[1][0][1]
                mail = email.message_from_bytes(e)

                login = re.search(regexlogin, mail['From'])
                login = login.group(1) if login else None

                hash = re.search(regexhash, mail['Subject'])
                hash = hash.group(1) if hash else None

                id_discord = await database.confirm_email(hash, login)
                if id_discord:
                    await logs.email_confimed(client, login, hash, id_discord)
                    await utils.new_confirmed_user(client, id_discord, login, config, database)
                else:
                    await logs.invalid_email(client, mail['From'], mail['Subject'])

                imap.copy(num,  config['email']['trash'])
                imap.store(num, '+FLAGS', r'(\Deleted)')
            imap.expunge()

    l = logging.getLogger('discord.admin.logout')
    l.info('email thread shutdown')

    if not client.is_closed:
        l.info('bot shutdown')
        await client.logout()
