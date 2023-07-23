import os
import sys
from utils.nginx.main import create_nginx, create_proxy_nginx, delete_ngnix
from utils.common import handle_html, handle_django
from utils.docker.common import clone_project, check_project_framework_from_path
import logging
from server.models import ProjectModel
from dotenv import load_dotenv
from fastapi import Body, Depends, HTTPException, status, File, UploadFile,Request
from fastapi.encoders import jsonable_encoder

from server.authentication import decode_token
from server.database import database
from utils.docker.common import restart_docker_project,write_env
import os
from bson import ObjectId

#
root_dir = "/var/www/html/"
nginx_root = "/etc/nginx/sites-enabled"
logger = logging.getLogger(__name__)

load_dotenv()

MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
USER_COLLECTION = os.environ.get('USER_COLLECTION')
PROJECT_COLLECTION = os.environ.get("PROJECT_COLLECTION")
CATEGORY_COLLECTION = os.environ.get("CATEGORY_COLLECTION")

proj_coll = database[PROJECT_COLLECTION]
user_coll = database[USER_COLLECTION]
cat_coll = database[CATEGORY_COLLECTION]
# root_dir = "/home/sunith/Documents/projects/next/drop-backend/"
# nginx_root = "/home/sunith/Documents/projects/next/drop-backend/nginx"

def create_project_task(envText: str, projects: ProjectModel,user_id:str):
    projects.id = str(ObjectId())
    projects.domain+=".radr.in"
    projects.build_status=2
    print(f"{projects.id =}\n")
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

    try:
        # adding category to DB
        # Check if the category already exists for the user
        existing_category = cat_coll.find_one({"name": projects.category, "user_id": user_id})
        #
        if existing_category is None:
            #     # Category doesn't exist, insert a new document
            new_category = {"name": projects.category, "user_id": user_id}
            cat_coll.insert_one(new_category)

    except Exception as e:
        print(f"{e =}\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not added",
        )

    created_list_item = created_list_item["projects"]
    # get last port
    pro = proj_coll.find()
    count = 0
    for p in pro:
        count += len(p["projects"])

    print(f"{count =}")
    proj_coll.update_one(
    {"user_id": user_id, "projects.id": projects.id},
    {"$set": {"projects":{"port":8000+count} }}
    )
    print(f"{projects.url =} {username =} {projects.id =} {projects.pname =} {projects =}")
    create_project(projects.url,username,projects.id, projects.domain, 8000 + count)

    print("project created\n")
    write_env(projects.path, convert_env_content(envText))
    restart_docker_project(f"projects/{projects.id}")

    try:
        return [ProjectModel(**item) for item in created_list_item]

    except Exception as e:
        print(f"{e =}\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project not added",
        )
    
def create_project(url, user, proj_name, domain, port=8001, runcommand="python manage.py runserver 0.0.0.0:8000"):
    """
    :param runcommand:
    :param port:
    :param url: git url
    :param user: username
    :param proj_name: project name
    :param domain: domain name
    :return: None
    """
    print(f"create_project: {url}, {user}, {proj_name}, {domain}, {port}, {runcommand}")
    clone_project(url=url, projects_folder="projects", project_name=proj_name)
    path = f"projects/{proj_name}"
    framework = check_project_framework_from_path(path=path)
    print(f"{framework = }")
    if framework == 'html':
        handle_html(path=path, domain=domain)
    elif framework == 'django':
        handle_django(path=path, domain=domain, port=port, runcommand=runcommand)



def delete_project(user, proj_name, domain):
    print(f"delete_project: {user}, {proj_name}, {domain}")
    path = f"projects/{proj_name}"
    os.system("rm -r {}".format(path))
    os.system("rm -r {}{}".format(root_dir, proj_name))
    delete_ngnix(domain=domain)
    print(f"delete_project: {user}, {proj_name}, {domain} deleted")


def convert_env_content(env_content: str):
    lines = env_content.strip().split('\n')
    env_data = {}

    for line in lines:
        key, value = line.split('=', 1)
        env_data[key.strip()] = value.strip()

    return env_data

if __name__ == "__main__":
    create_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
