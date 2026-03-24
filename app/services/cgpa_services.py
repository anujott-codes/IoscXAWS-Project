from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.model import models


def extract_sem_wise_cgpa(record):
    data = []

    for i in range(1, 9):
        cgpa = getattr(record, f"sem{i}_cgpa")
        backlogs = getattr(record, f"sem{i}_backlogs")

        if cgpa is None and backlogs == 0:
            continue  

        data.append({
            "semester": i,
            "cgpa": float(cgpa) if cgpa is not None else None,
            "backlogs": backlogs
        })

    return data


async def get_cgpa_progress(student_id: int, db: AsyncSession):
    result = await db.execute(
        select(models.AcademicRecords)
        .where(models.AcademicRecords.student_id == student_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        return None

    return extract_sem_wise_cgpa(record)


async def get_cgpa_analytics(student_id: int, db: AsyncSession):
    result = await db.execute(
        select(models.AcademicRecords)
        .where(models.AcademicRecords.student_id == student_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        return None

    sem_data = extract_sem_wise_cgpa(record)

    if not sem_data:
        return {
            "average_cgpa": None,
            "highest_cgpa": None,
            "lowest_cgpa": None,
            "total_backlogs": 0,
            "cgpa_trend": []
        }

    cgpas = [d["cgpa"] for d in sem_data if d["cgpa"] is not None]
    backlogs = [d["backlogs"] for d in sem_data]

    return {
        "average_cgpa": sum(cgpas) / len(cgpas) if cgpas else None,
        "highest_cgpa": max(cgpas) if cgpas else None,
        "lowest_cgpa": min(cgpas) if cgpas else None,
        "total_backlogs": sum(backlogs),
        "cgpa_trend": cgpas
    }