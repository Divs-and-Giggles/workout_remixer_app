from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pydantic import EmailStr
from pwdlib import PasswordHash

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    routines: list['Routine'] = Relationship(back_populates = "user")
    sessions: list['WorkoutSession'] = Relationship(back_populates = "user")

    def check_password(self, plaintext_password:str):
        return PasswordHash.recommended().verify(password=plaintext_password, hash=self.password)
    
class AdminCreate(UserBase):
    role:str = "admin"

class RegularUserCreate(UserBase):
    role:str = "regular_user"