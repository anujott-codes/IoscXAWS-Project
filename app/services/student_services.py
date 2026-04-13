from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
import app.model.models as models
from sqlalchemy.orm import selectinload
import app.schema.schemas as schemas
from app.services.file_services import save_file
from typing import Optional


# get student basic
async def get_student_basic(db: AsyncSession, student_id: str):
    result = await db.execute(
        select(models.Student).where(models.Student.roll_number == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise ValueError("Student not found")
    return student


# get student full profile
async def get_student_full(db: AsyncSession, student_id: str):
    result = await db.execute(
        select(models.Student)
        .where(models.Student.roll_number == student_id)
        .options(
            selectinload(models.Student.classification),
            selectinload(models.Student.parent_details),
            selectinload(models.Student.academic_records),
            selectinload(models.Student.financial_info),
            selectinload(models.Student.documents),
            selectinload(models.Student.noc_records),
            selectinload(models.Student.placement),
            selectinload(models.Student.academic_documents),
            selectinload(models.Student.internships),
            selectinload(models.Student.research_papers),
        )
    )
    student = result.scalar_one_or_none()
    if not student:
        raise ValueError("Student not found")
    return student


# create new student
async def create_student(db: AsyncSession, student_data):
    student = models.Student(**student_data.model_dump())
    db.add(student)
    try:
        await db.commit()
        await db.refresh(student)
        return student
    except Exception:
        await db.rollback()
        raise


# ------------------ LIST ------------------
async def list_students(
    db: AsyncSession, 
    branch: Optional[str] = None, 
    year: Optional[int] = None,
    category: Optional[str] = None,
    is_hosteller: Optional[bool] = None,
    is_placed: Optional[bool] = None,
    scholarship: Optional[str] = None
):
    query = select(models.Student)

    if category is not None or is_hosteller is not None:
        query = query.join(models.StudentClassification, models.Student.roll_number == models.StudentClassification.student_id, isouter=True)
        if category is not None:
            query = query.where(models.StudentClassification.category == category)
        if is_hosteller is not None:
            query = query.where(models.StudentClassification.is_hosteller == is_hosteller)
            
    if is_placed is not None:
        query = query.join(models.Placement, models.Student.roll_number == models.Placement.student_id, isouter=True)
        query = query.where(models.Placement.is_placed == is_placed)
        
    if scholarship is not None:
        query = query.join(models.FinancialInfo, models.Student.roll_number == models.FinancialInfo.student_id, isouter=True)
        if scholarship.lower() == "none" or scholarship == "":
            from sqlalchemy import or_
            query = query.where(
                or_(
                    models.FinancialInfo.scholarship_type == "None", 
                    models.FinancialInfo.scholarship_type == None
                )
            )
        else:
            query = query.where(models.FinancialInfo.scholarship_type == scholarship)

    if branch:
        query = query.where(models.Student.branch == branch)
    if year:
        query = query.where(models.Student.year == year)

    result = await db.execute(query)
    return result.unique().scalars().all()


# update existing student
async def update_student(db: AsyncSession, student_id: str, data: schemas.StudentUpdate):
    student = await get_student_basic(db, student_id)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(student, key, value)

    try:
        await db.commit()
        await db.refresh(student)
        return student
    except Exception:
        await db.rollback()
        raise


# delete student
async def delete_student(db: AsyncSession, student_id: str):
    student = await get_student_basic(db, student_id)

    try:
        # Delete all related records in dependency order using cascade strategy
        await db.execute(delete(models.StudentClassification).where(models.StudentClassification.student_id == student_id))
        await db.execute(delete(models.ParentDetails).where(models.ParentDetails.student_id == student_id))
        await db.execute(delete(models.AcademicRecords).where(models.AcademicRecords.student_id == student_id))
        await db.execute(delete(models.FinancialInfo).where(models.FinancialInfo.student_id == student_id))
        await db.execute(delete(models.Internship).where(models.Internship.student_id == student_id))
        await db.execute(delete(models.ResearchPaper).where(models.ResearchPaper.student_id == student_id))
        await db.execute(delete(models.Documents).where(models.Documents.student_id == student_id))
        await db.execute(delete(models.NocRecords).where(models.NocRecords.student_id == student_id))
        await db.execute(delete(models.Placement).where(models.Placement.student_id == student_id))
        await db.execute(delete(models.AcademicDocuments).where(models.AcademicDocuments.student_id == student_id))
        
        # Delete corresponding user account from auth table
        await db.execute(delete(models.DBUser).where(models.DBUser.username == student_id))
        
        # Finally delete the student record itself
        await db.execute(delete(models.Student).where(models.Student.roll_number == student_id))
        
        await db.commit()
        return {"detail": "Student deleted"}
    except Exception:
        await db.rollback()
        raise


# upload photo
async def upload_photo(db: AsyncSession, student_id: str, photo):
    student = await get_student_basic(db, student_id)

    student.photo_path = save_file(student_id, photo)

    try:
        await db.commit()
        return {"photo_path": student.photo_path}
    except Exception:
        await db.rollback()
        raise

# upload signature
async def upload_signature(db: AsyncSession, student_id: str, signature):
    student = await get_student_basic(db, student_id)

    student.signature_path = save_file(student_id, signature)

    try:
        await db.commit()
        return {"signature_path": student.signature_path}
    except Exception:
        await db.rollback()
        raise
