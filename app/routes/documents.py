from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

import app.schema.schemas as schemas
from app.core.database import get_db
from app.services import document_services
from app.services.authorization_services import verify_user_access


router = APIRouter(
    prefix="/students/{student_id}/documents",
    tags=["Documents"],
    dependencies=[Depends(verify_user_access)]
)


@router.post("/", response_model=schemas.DocumentsResponse)
async def create_documents(
    student_id: str,
    data: schemas.DocumentsCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await document_services.create_documents(db, student_id, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=schemas.DocumentsResponse)
async def update_documents(
    student_id: str,
    data: schemas.DocumentsCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await document_services.update_documents(db, student_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=schemas.DocumentsResponse)
async def get_documents(
    student_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await document_services.get_documents(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/upload")
async def upload_documents(
    student_id: str,
    aadhaar: Optional[UploadFile] = File(None),
    pan: Optional[UploadFile] = File(None),
    id_card: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await document_services.upload_documents(
            db,
            student_id,
            aadhaar,
            pan,
            id_card
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/download/{file_type}", dependencies=[])
async def download_document(
    student_id: str,
    file_type: str,
    db: AsyncSession = Depends(get_db)
):
    if file_type not in ["aadhaar", "pan", "id_card"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    try:
        doc = await document_services.get_documents(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    path_map = {
        "aadhaar": doc.aadhaar_path,
        "pan": doc.pan_path,
        "id_card": doc.id_card_path,
    }
    path = path_map[file_type]
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))

# Public router for file downloads (no auth — token passed as query param instead)
public_router = APIRouter(
    prefix="/students/{student_id}/documents",
    tags=["Documents"],
)

@public_router.get("/download/{file_type}")
async def download_document_public(
    student_id: str,
    file_type: str,
    db: AsyncSession = Depends(get_db)
):
    if file_type not in ["aadhaar", "pan", "id_card"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    try:
        doc = await document_services.get_documents(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    path_map = {
        "aadhaar": doc.aadhaar_path,
        "pan": doc.pan_path,
        "id_card": doc.id_card_path,
    }
    path = path_map[file_type]
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=os.path.basename(path))