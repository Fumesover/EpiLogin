import asyncpg
import asyncio

import logs

class database:
    def __init__(self):
        self.conn = None

    async def init(self, config):
        try:
            self.conn = await asyncpg.connect(config['database']['url']) # 'postgresql://postgres@localhost/postgres'
        except:
            await asyncio.sleep(30) # Wait for database
            self.conn = await asyncpg.connect(config['database']['url']) # 'postgresql://postgres@localhost/postgres'

        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users(
                id BIGINT PRIMARY KEY UNIQUE,
                login TEXT,
                hash TEXT,
                confirmed INTEGER
            )
        ''')

        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS groupes(
                id SERIAL PRIMARY KEY,
                login text,
                groupe text
            )
        ''')

    async def close(self):
        await self.conn.close()

    async def get_login(self, discord_id):
        login = await self.conn.fetchrow('''
            SELECT login FROM users WHERE id = $1
        ''', int(discord_id))

        return login['login'] if login else None

    async def get_hash(self, id):
        data = await self.conn.fetchrow("""
            SELECT hash FROM users WHERE id = $1
        """, int(id))

        return data['hash'] if data else None

    async def get_groups(self, login):
        data = await self.conn.fetch('''
            SELECT groupe FROM groupes WHERE login = $1
        ''', login)

        return [ g['groupe'] for g in data ]

    async def get_ids(self, login):
        data = await self.conn.fetch('''
            SELECT id FROM users WHERE login = $1
        ''', login)

        return [e['id'] for e in data]

    async def add_user(self, discord_id, hash):
        await self.conn.execute('''
            INSERT INTO users(id, hash, confirmed)
                    VALUES   ($1,   $2,         0)
        ''', int(discord_id), hash)

    async def del_user(self, discord_id):
        await self.conn.execute('''
            DELETE FROM users WHERE id = $1
        ''', int(discord_id))

    async def confirm_email(self, hash, login):
        if not hash or not login:
            return False

        # 1 -> Get user id using hash
        data = await self.conn.fetch('''
            SELECT id FROM users WHERE hash = $1
        ''', hash)

        if len(data) == 0:
            await logs.email_unknown_hash(hash, login)
            return False

        await self.conn.execute('''
            UPDATE users
            SET confirmed = $1, login = $2, hash = $3
            WHERE id = $4
        ''', 1, login, '', data[0]['id'])

        return data[0]['id']

    async def add_groups(self, login, groups):
        for group in groups:
            await self.conn.execute('''
                INSERT INTO groupes(login, groupe) values($1, $2)
            ''', login, group)
        if groups:
            await logs.database_add_groups(login, groups)

    async def del_groups(self, login, groups):
        for group in groups:
            await self.conn.execute('''
                DELETE FROM groupes WHERE login = $1 AND groupe = $2
            ''', login, group)
        if groups:
            await logs.database_del_groups(login, groups)
