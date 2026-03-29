import asyncio
from app.core.database import SessionLocal
from app.model.models import DBUser
from sqlalchemy import select, func

async def count_by_role():
    async with SessionLocal() as db:
        result = await db.execute(
            select(DBUser.role, func.count().label("count"))
            .group_by(DBUser.role)
        )
        rows = result.all()
        for role, count in rows:
            print(f"{role}: {count}")

asyncio.run(count_by_role())