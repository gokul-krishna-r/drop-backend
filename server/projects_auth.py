from fastapi import APIRouter, Body, Depends, HTTPException, status,File,UploadFile
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from .models import ProjectModel
from.authentication import decode_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import database
import razorpay
import os
from bson.binary import Binary
from bson import ObjectId



load_dotenv()

router = APIRouter()
MONGO_DB_NAME=os.environ.get('MONGO_DB_NAME')
ALGORITHM=os.environ.get("ALGORITHM")
SECRET_KEY= os.environ.get('SECRET_KEY')
USER_COLLECTION=os.environ.get('USER_COLLECTION')
PROJECT_COLLECTION=os.environ.get("PROJECT_COLLECTION")


proj_coll=database[PROJECT_COLLECTION]
user_coll=database[USER_COLLECTION]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")



@router.post("/create_project/",response_model=list[ProjectModel])
async def create_project(projects: ProjectModel = Body(...),token:str=Depends(decode_token)):
    user = user_coll.find_one({"email_id":token})
    if not user:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    projects.id=str(ObjectId())
    user_id=user["_id"]
    proj=proj_coll.find_one({"user_id":user_id})
    if proj:
        new_list_item = proj_coll.update_one({"user_id":user_id},{"$push":{"projects":jsonable_encoder(projects)}})
        if new_list_item.modified_count == 0:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not added",
            )
    else:
        new_list_item = proj_coll.insert_one({"user_id":user_id,"projects":[jsonable_encoder(projects)]})   


    created_list_item = proj_coll.find_one({
        "user_id": user_id
    }) 
    created_list_item=created_list_item["projects"]   
      
    return [ProjectModel(**item) for item in created_list_item]
    

@router.get("/list_projects/",response_model=list[ProjectModel])
async def list_projects(token:str=Depends(decode_token)):
    user = user_coll.find_one({"email_id":token})
    if not user:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id=user["_id"]
    created_list_item = proj_coll.find_one({
        "user_id": user_id
    }) 
    created_list_item=created_list_item["projects"]   
      
    return [ProjectModel(**item) for item in created_list_item]

@router.get("/get_porject/",response_model=ProjectModel)
async def get_project(project_id,token:str=Depends(decode_token)):
    user = user_coll.find_one({"email_id":token})
    if not user:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id=user["_id"]
    project = proj_coll.find_one(
        {"user_id": user_id, "projects": {"$elemMatch": {"id": project_id}}}
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    project = [p for p in project["projects"] if p["id"] == project_id][0]

    return ProjectModel(**project)


    

