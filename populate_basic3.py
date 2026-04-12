import asyncio
import json
from app.core.database import SessionLocal
from app.model.models import Student, ParentDetails
from sqlalchemy import select

async def populate_basic():
    with open("basic3.json", "r") as f:
        data = json.load(f)

    async with SessionLocal() as db:
        created = 0
        updated = 0
        failed = 0

        for i, entry in enumerate(data):
            roll_number = entry["roll_number"]
            try:
                # Handle student record
                result = await db.execute(select(Student).filter(Student.roll_number == roll_number))
                student = result.scalars().first()

                if student:
                    student.name = entry["name"]
                    student.branch = entry["branch"]
                    student.year = entry["year"]
                    await db.commit()
                    updated += 1
                    print(f"[{i+1}/{len(data)}] Updated student: {roll_number}")
                else:
                    new_student = Student(
                        roll_number=roll_number,
                        name=entry["name"],
                        branch=entry["branch"],
                        year=entry["year"],
                        email=f"{roll_number}@estudentcell.local",
                        mobile="0000000000",
                    )
                    db.add(new_student)
                    await db.commit()
                    created += 1
                    print(f"[{i+1}/{len(data)}] Created student: {roll_number}")

                # Handle parent record
                parent_result = await db.execute(select(ParentDetails).filter(ParentDetails.student_id == roll_number))
                parent = parent_result.scalars().first()

                if parent:
                    parent.parent_name = entry["parent_name"]
                    await db.commit()
                    print(f"[{i+1}/{len(data)}] Updated parent: {roll_number}")
                else:
                    new_parent = ParentDetails(
                        student_id=roll_number,
                        parent_name=entry["parent_name"],
                    )
                    db.add(new_parent)
                    await db.commit()
                    print(f"[{i+1}/{len(data)}] Created parent: {roll_number}")

            except Exception as e:
                print(f"[{i+1}/{len(data)}] Failed: {roll_number} — {e}")
                await db.rollback()
                failed += 1

        print(f"\nDone. Created: {created}, Updated: {updated}, Failed: {failed}")

asyncio.run(populate_basic())