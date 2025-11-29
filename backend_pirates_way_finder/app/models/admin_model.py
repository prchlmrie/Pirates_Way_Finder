from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminBase(BaseModel):
    email: EmailStr

class AdminCreate(AdminBase):
    password: str
    full_name: Optional[str] = None

class AdminLogin(AdminBase):
    password: str