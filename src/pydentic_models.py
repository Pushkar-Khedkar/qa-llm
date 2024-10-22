from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserCreate(BaseModel):
    first_name:str
    last_name:str
    email: EmailStr
    created_at: datetime = datetime.now()
    password: str

    class Config():
        from_attributes = True

class UserCreds(BaseModel):
    email:str
    password:str
    

class SuccessHandler(BaseModel):
    success: bool = True
    message: str = 'Operation successful'
    data: Optional[dict] = None


class ErrorHandler(BaseModel):
    success: bool = True
    message: str = 'Operation failed'
    errors: Optional[List[dict]] = None

