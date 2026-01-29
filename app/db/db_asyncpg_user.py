from typing import List, Optional
from app.db.db_asyncpg import db
from app.schemas.user_schema import User

async def get_user_by_email(email: str) -> Optional[User]:
    query = "SELECT name, email FROM users WHERE email = $1"
    async with db.pool.acquire() as connection:
        row = await connection.fetchrow(query, email)
        if row is not None:
            user = User(name=row["name"], email=row["email"]) 
            return user
        return None


async def get_all_users(limit: int, offset: int) -> List[User]:
    query = "SELECT name, email FROM users LIMIT $1 OFFSET $2"
    async with db.pool.acquire() as connection:
        rows = await connection.fetch(query, limit, offset)
        users = [User(name=record["name"], email=record["email"]) for record in rows]
        return users


async def insert_user(user: User):
    query = "INSERT INTO users (name, email) VALUES ($1, $2)"
    async with db.pool.acquire() as connection:
        await connection.execute(query, user.name, user.email)


async def bulk_insert_users(users: List[User]):
    query = "INSERT INTO users (name, email) VALUES ($1, $2)"
    user_tuples = [(user.name, user.email) for user in users]
    async with db.pool.acquire() as connection:
        await connection.executemany(query, user_tuples)