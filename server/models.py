from typing import Optional
from bson import ObjectId
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, Field
from enum import Enum
import uuid


def generate_uuid():
    return str(uuid.uuid4()[:6]).replace("-", "")


class UserModelOut(BaseModel):
    fname: str = Field(...)
    lname: str = Field(...)
    email_id: str = Field(default=...)

    class Config:
        schema_extra = {
            "example": {
                "fname": "John",
                "lname": "Thrikkakara",
                "email_id": 'jdoe@hotmail.com',
            }
        }


class UserModel(UserModelOut):
    fname: str = Field(...)
    lname: str = Field(...)
    email_id: str = Field(default=...)
    password: str = Field(...)
    deleted: int | None = Field(default=0)

    class Config:
        schema_extra = {
            "example": {
                "fname": "John",
                "lname": "Thrikkakara",
                "email_id": 'jdoe@hotmail.com',
                "password": "passpass",
                "deleted": 0
            }
        }


class ProjectModel(BaseModel):
    id: str | None = Field(description="optional")
    pname: str = Field(...)
    domain: str = Field(...)
    build_status: int = Field(default=0, description="""0:Initial
    1:Deploying
    2:Running
    3:Suspened
    4:Destroyed""")
    build_cmd: str = Field(...)
    start_cmd: str = Field(...)
    url: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "pname": "p1",
                "domain": "www.p1.drop.me",
                "build_status": '0',
                "build_cmd": "npm install",
                "start_cmd": "npm run dev"
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "accestoken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NGQ1OWNlZi1kYmI4LTRlYTUtYjE3OC1kMjU0MGZjZDY5MTkiLCJqdGkiOiI2Yj",
                "token_type": "Bearer",
            }
        }


class TokenData(BaseModel):
    username: str | None = None


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
