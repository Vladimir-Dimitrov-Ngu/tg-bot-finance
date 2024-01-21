import aiosqlite
import config


async def get_data_from_db(sql):
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql) as cursor:
            return cursor.fetchone()


async def insert_into_db(
    sql,
):
    async with aiosqlite.connect(config.SQLITE_DB_FILE) as db:
        await db.execute(sql)
        await db.commit()
