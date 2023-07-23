import random

from fastapi import APIRouter, Body, Depends, HTTPException, status, File, UploadFile,Request,BackgroundTasks
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv


from utils.docker.common import write_env, read_env, pull_project,start_docker_project,stop_docker_project,check_project_framework_from_path,restart_docker_project
from utils.docker.django import start_django_project
from utils.pull import git_pull
from .models import ProjectModel
from .authentication import decode_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from .database import database
import razorpay
import os
from bson.binary import Binary
from bson import ObjectId
from utils.create_project import convert_env_content
from utils.create_project import create_project as create_proj
from utils.create_project import delete_project as delete_proj
from utils.create_project import create_project_task

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


@router.post("/create_project/")
async def create_project(background_tasks: BackgroundTasks,envText: str = Body(default=""), projects: ProjectModel = Body(...),
                         token: str = Depends(decode_token)):
    # log_file = open("log.txt", "a")
    print("create_project\n")
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = user["_id"]
    proj=proj_coll.find_one({"user_id": user_id})
    pro = proj_coll.find()

    if(proj==None):
        print("no project")
    else:
        for p in pro:
            print(p["projects"])
            for j in p["projects"]:
                if projects.domain+".radr.in"==(j["domain"]):
                    raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project with same domain exists",
                    )
        for p in proj["projects"]:
            if projects.pname==p["pname"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Project with same name exists",
                    )

    background_tasks.add_task(create_project_task, envText, projects,user_id)

    return {"message": "Project creation started"}




@router.post("/delete_project/", response_model=list[ProjectModel])
async def delete_project(project_domain: str = Body(...), project_id: str = Body(...),
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
    projects_cat=proj_coll.find_one({"user_id": user_id, "projects.domain": project_domain})["projects"][0]["category"]

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
    delete_category(projects_cat, user_id)
    stop_docker_project(f"projects/{project_id}")
    delete_proj(username, project_id, project_domain)
    print("project deleted\n")

    
    return [ProjectModel(**item) for item in created_list_item]


@router.post("/suspend_project/{project_id}",response_model=list[ProjectModel])
async def suspend_project(background_tasks: BackgroundTasks,project_id: str,token: str = Depends(decode_token)):
    print(project_id)

    user = user_coll.find_one({"email_id": token})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(project_id)
    background_tasks.add_task(stop_docker_project, f"projects/{project_id}")
    user_id=user["_id"]
    result = proj_coll.update_one(
    {"user_id": user_id, "projects.id": project_id},
    {"$set": {"projects.$.build_status": 3}}
    )
    created_list_item = proj_coll.find_one({
        "user_id": user_id
    })

    created_list_item = created_list_item["projects"]
    return [ProjectModel(**item) for item in created_list_item]


@router.post("/resume_project/{project_id}",response_model=list[ProjectModel])
async def resume_project(background_tasks: BackgroundTasks,project_id: str,token: str = Depends(decode_token)):
    user = user_coll.find_one({"email_id": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    framework = check_project_framework_from_path(f"projects/{project_id}")
    if framework == "django":
        background_tasks.add_task(start_django_project, f"projects/{project_id}")
    elif framework == "html":
        print('html')
        background_tasks.add_task(start_docker_project,f"projects/{project_id}")

    user_id=user["_id"]
    result = proj_coll.update_one(
    {"user_id": user_id, "projects.id": project_id},
    {"$set": {"projects.$.build_status": 2}}
    )
    created_list_item = proj_coll.find_one({
        "user_id": user_id
    })

    created_list_item = created_list_item["projects"]
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


@router.post("/env/", response_model=dict)
async def post_env(project_id: str = Body(...), env: str = Body(...), token: str = Depends(decode_token)):
    print("post_env\n")
    print(env)
    write_env(f"projects/{project_id}", convert_env_content(env))

    return {"message": "Environment variables updated"}


@router.get("/env/", response_model=dict)
async def get_env(project_id: str = Body(...), token: str = Depends(decode_token)):
    print("get_env\n")
    env = read_env(f"projects/{project_id}")
    return env




@router.post("/git_pull/{project_id}/", response_model=dict)
async def git_pull(project_id: str):
    print("git_pull\n")
    print(project_id)
    pull_project(f"projects/{project_id}")
    return {"message": "Git pull successful"}

@router.post("/del_category/", response_model=dict)
async def del_cat(token=Depends(decode_token), project_cat: str = Body(...)):
    user = user_coll.find_one({"email_id": token})
    user_id = user["_id"]
    delete_category(project_cat, user_id)
    categories = cat_coll.find({"user_id": user_id})

    # Convert categories to a list and exclude MongoDB's internal _id field
    categories_list = [category["name"] for category in categories]

    return {"categories": categories_list}

def delete_category(project_cat, user_id):
    try:
    # adding category to DB
        # Check if the category already exists for the user
        print(project_cat)

        count = proj_coll.count_documents({"user_id": user_id,"projects.category": project_cat})
        print(count)
        if count == 0 :
            #   Category doesn't exist, insert a new document
            cat_coll.delete_one({"name": project_cat, "user_id": user_id})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not deleted",
        )

