from app.services.common_services import user_add
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.db import get_db
from app.schemas.schema import  CommonResponse

router = APIRouter()

# @router.post("/add/users/", response_model=CommonResponse)
# def create_user(user: UserBase, db: Session = Depends(get_db)):
#     try:
       
#         new_user = user_add(user=user, db=db)
        

#         return CommonResponse(
#             status=201,
#             data=new_user,
#             msg="User created successfully"
#         )
#     except Exception as e:
#         return CommonResponse(
#             status=500,
#             data=str(e),
#             msg="Something went wrong"
#         )
