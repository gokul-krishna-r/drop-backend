import random

from fastapi import APIRouter, Body, Depends, HTTPException, status, File, UploadFile
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv
from .models import ProjectModel
from .authentication import decode_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import database
import razorpay
import os
from bson.binary import Binary
from bson import ObjectId
from utils.create_project import create_project as create_proj
from utils.create_project import delete_project as delete_proj

load_dotenv()

router = APIRouter()
MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
ALGORITHM = os.environ.get("ALGORITHM")
SECRET_KEY = os.environ.get('SECRET_KEY')
USER_COLLECTION = os.environ.get('USER_COLLECTION')
PROJECT_COLLECTION = os.environ.get("PROJECT_COLLECTION")
CATEGORY_COLLECTION = os.environ.get("CATEGORY_COLLECTION")

proj_coll = database[PROJECT_COLLECTION]
user_coll = database[USER_COLLECTION]
cat_coll = database[CATEGORY_COLLECTION]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


@router.post("/create_project/", response_model=list[ProjectModel])
async def create_project(projects: ProjectModel = Body(...), token: str = Depends(decode_token)):
    # log_file = open("log.txt", "a")

    print("create_project\n")
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    projects.id = str(ObjectId())
    print(f"{projects.id =}\n")
    user_id = user["_id"]
    proj = proj_coll.find_one({"user_id": user_id})
    print(f"{proj =}\n")
    if proj:
        print("project exists\n")
        new_list_item = proj_coll.update_one({"user_id": user_id}, {"$push": {"projects": jsonable_encoder(projects)}})
        if new_list_item.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project not added",
            )

    else:
        new_list_item = proj_coll.insert_one({"user_id": user_id, "projects": [jsonable_encoder(projects)]})

    created_list_item = proj_coll.find_one({
        "user_id": user_id
    })
    username = user_coll.find_one({
        "_id": user_id
    }).get("fname")
    print("koi")

    # adding category to DB
    # Check if the category already exists for the user
    # existing_category = cat_coll.find_one({"name": projects.category, "user_id": user_id})
    #
    # if existing_category is None:
    #     # Category doesn't exist, insert a new document
    #     new_category = {"name": projects.category, "user_id": user_id}
    #     cat_coll.insert_one(new_category)
    # else:
    #     raise HTTPException(status_code=400, detail="Category already exists")

    created_list_item = created_list_item["projects"]
    # get last port
    projects = proj_coll.find()
    count = 0
    for p in projects:
        count += len(p["projects"])

    print(f"{count =}")

    print(f"{projects.url =} {username =} {projects.id =} {projects.pname =} {projects =}")
    create_proj(projects.url, username, projects.id, projects.domain, 8000 + count)

    print("project created\n")
    try:
        return [ProjectModel(**item) for item in created_list_item]

    except Exception as e:
        print(f"{e =}\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not added",
        )


@router.post("/delete_project/", response_model=list[ProjectModel])
async def delete_project(project_domain: str = Body(...), project_name: str = Body(...),
                         token: str = Depends(decode_token)):
    print("delete_project\n")
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = user["_id"]
    proj = proj_coll.find_one({"user_id": user_id})
    if proj:
        new_list_item = proj_coll.update_one({"user_id": user_id}, {"$pull": {"projects": {"domain": project_domain}}})
        if new_list_item.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project not deleted",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not deleted",
        )

    created_list_item = proj_coll.find_one({
        "user_id": user_id
    })
    username = user_coll.find_one({
        "_id": user_id
    }).get("fname")
    created_list_item = created_list_item["projects"]
    delete_proj(username, project_name, project_domain)
    print("project deleted\n")
    return [ProjectModel(**item) for item in created_list_item]


@router.get("/list_projects/", response_model=list[ProjectModel])
async def list_projects(token: str = Depends(decode_token)):
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = user["_id"]
    created_list_item = proj_coll.find_one({
        "user_id": user_id
    })
    if not created_list_item:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail="User project empty",
            headers={"WWW-Authenticate": "Bearer"},
        )

    created_list_item = created_list_item["projects"]

    return [ProjectModel(**item) for item in created_list_item]


@router.get("/get_project/", response_model=ProjectModel)
async def get_project(project_id, token: str = Depends(decode_token)):
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = user["_id"]
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


@router.get("/get_categories/")
async def list_categories(token: str = Depends(decode_token)):
    # Query categories collection to retrieve categories for the user
    user = user_coll.find_one({"email_id": token})
    user_id = user["_id"]
    categories = cat_coll.find({"user_id": user_id})

    # Convert categories to a list and exclude MongoDB's internal _id field
    categories_list = [category["name"] for category in categories]

    return {"categories": categories_list}
