import asyncio
from app.core.database import SessionLocal
from app.model.models import DBUser, RoleEnum
from sqlalchemy import delete

async def delete_students():
    async with SessionLocal() as db:
        result = await db.execute(
            delete(DBUser).where(DBUser.role == RoleEnum.student)
        )
        await db.commit()
        print(f"Deleted {result.rowcount} students")

asyncio.run(delete_students())