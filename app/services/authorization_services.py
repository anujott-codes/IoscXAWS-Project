from fastapi import Path, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.authHelper import DBUser, get_current_user, RoleEnum, get_db
from app.model.models import Student

async def verify_user_access(
    student_id: int = Path(...), 
    current_user: DBUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if str(current_user.role) == RoleEnum.admin:
        return current_user
        
    if str(current_user.role) == RoleEnum.student:
        result = await db.execute(select(Student).filter(Student.id == student_id))
        target_student = result.scalars().first()
        
        if not target_student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if str(current_user.username) != str(target_student.roll_number):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view or edit this student's data"
            )
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have permission to view or edit this student's data"
    )
