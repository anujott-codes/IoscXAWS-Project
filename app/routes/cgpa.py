from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import cgpa_services
from app.schema.schemas import CGPAEntry, CGPAAnalytics
from app.core.database import get_db
from typing import List

router = APIRouter(prefix="/students", tags=["CGPA"])


@router.get("/{student_id}/cgpa", response_model=List[CGPAEntry])
async def cgpa_progress(student_id: int, db: AsyncSession = Depends(get_db)):
    data = await cgpa_services.get_cgpa_progress(student_id, db)

    if data is None:
        raise HTTPException(status_code=404, detail="Academic record not found")

    return data


@router.get("/{student_id}/cgpa/analytics", response_model=CGPAAnalytics)
async def cgpa_analytics(student_id: int, db: AsyncSession = Depends(get_db)):
    data = await cgpa_services.get_cgpa_analytics(student_id, db)

    if data is None:
        raise HTTPException(status_code=404, detail="Academic record not found")

    return data