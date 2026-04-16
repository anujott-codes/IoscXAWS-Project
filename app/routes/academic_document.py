from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

import app.schema.schemas as schemas
from app.core.database import get_db
from app.services import academic_document_services
from app.services.authorization_services import verify_user_access


router = APIRouter(
    prefix="/students/{student_id}/academic-documents",
    tags=["Academic Documents"],
    dependencies=[Depends(verify_user_access)]
)


@router.post("/", response_model=schemas.AcademicDocsResponse)
async def create_academic_docs(
    student_id: str,
    data: schemas.AcademicDocsCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await academic_document_services.create_academic_docs(db, student_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=schemas.AcademicDocsResponse)
async def update_academic_docs(
    student_id: str,
    data: schemas.AcademicDocsCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await academic_document_services.update_academic_docs(db, student_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=schemas.AcademicDocsResponse)
async def get_academic_docs(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await academic_document_services.get_academic_docs(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload")
async def upload_academic_docs(
    student_id: str,
    marksheets: Optional[UploadFile] = File(None),
    provisional_cert: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await academic_document_services.upload_academic_docs(
            db,
            student_id,
            marksheets,
            provisional_cert
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{file_type}", dependencies=[])
async def download_academic_doc(
    student_id: str,
    file_type: str,
    db: AsyncSession = Depends(get_db)
):
    if file_type not in ["marksheets", "provisional_cert"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    try:
        doc = await academic_document_services.get_academic_docs(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    path_map = {
        "marksheets": doc.marksheets_path,
        "provisional_cert": doc.provisional_cert_path,
    }
    path = path_map[file_type]
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))
