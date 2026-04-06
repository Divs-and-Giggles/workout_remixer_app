from sqlmodel import Field, SQLModel, Relationship
from typing import Optional
from pwdlib import PasswordHash
from pydantic import EmailStr

password_hash = PasswordHash.recommended()

class UserBase(SQLModel,):
    username: str = Field(index=True, unique=True)
    email: EmailStr = Field(index=True, unique=True)
    password: str
    role:str = ""

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    routines: list['Routine'] = Relationship(back_populates = "user")
    sessions: list['WorkoutSession'] = Relationship(back_populates = "user")
    
    
    def set_password(self, password):
          self.password = password_hash.hash(password)