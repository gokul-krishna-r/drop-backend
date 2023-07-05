import os
import logging

logger = logging.getLogger(__name__)


def check_project_framework_from_path(path):
    """
    :param path: project path
    :return: framework name
    """
    if os.path.exists(path + "/manage.py"):
        return "django"
    elif os.path.exists(path + "/package.json"):
        with open(path + "/package.json") as f:
            content = f.read()
            if "react" in content:
                return "react"
            elif "express" in content:
                return "express"
    elif os.path.exists(path + "/index.html"):
        return "html"
    elif os.path.exists(path + "/index.js"):
        return "node"
    else:
        return "unknown"


def checkout_to_project_folder():
    print("checkout_to_project_folder")
    os.chdir("/home/ubuntu/drop-backend")
    print(f"{os.getcwd() = }")


def clone_project(url, projects_folder="projects", project_name="django_project"):
    print(f"clone_project: {url}, {projects_folder}, {project_name}")
    os.system(f"git clone {url} {projects_folder}/{project_name}")
    os.chdir(f"{projects_folder}/{project_name}")
    print(f"cloned successful {os.getcwd() = }")
    checkout_to_project_folder()


def start_docker_project(path):
    checkout_to_project_folder()
    print(f"start_docker_project: {path}")
    os.chdir(f"{path}")
    os.system("docker compose up -d --build")
    print("docker build successful")
    checkout_to_project_folder()


def stop_docker_project(path):
    checkout_to_project_folder()
    print(f"stop_docker_project: {path}")
    os.chdir(f"{path}")
    os.system("docker compose down")
    print("docker stop successful")
    checkout_to_project_folder()


def pull_project(path):
    checkout_to_project_folder()
    print(f"pull_project: {path}")
    stop_docker_project(path)
    os.chdir(f"{path}")
    os.system("git pull")
    print("git pull successful")
    checkout_to_project_folder()
    framework = check_project_framework_from_path(path)
    if framework == "django":
        restart_docker_project(path)
    elif framework == "html":
        print('html')
        os.system(f"rm -r /var/www/html/{path.split('/')[-1]}")
        os.system(f"cp -r {path} /var/www/html/{path.split('/')[-1]}")


def restart_docker_project(path):
    checkout_to_project_folder()
    print(f"restart_docker_project: {path}")
    stop_docker_project(path)
    start_docker_project(path)
    print("docker restart successful")


def write_env(path, envs: dict):
    checkout_to_project_folder()
    print(f"write_env: {path}")
    os.chdir(f"{path}")
    with open(".env", "w") as f:
        for key, value in envs.items():
            f.write(f"{key}={value}\n")
    print("write_env successful")
    checkout_to_project_folder()


def read_env(path):
    checkout_to_project_folder()
    print(f"read_env: {path}")
    os.chdir(f"{path}")
    envs = {}
    with open(".env", "r") as f:
        for line in f.readlines():
            key, value = line.split("=")
            envs[key] = value
    print("read_env successful")
    checkout_to_project_folder()
    return envs
