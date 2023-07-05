import os
import logging

logger = logging.getLogger(__name__)


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
    start_docker_project(path)


def restart_docker_project(path):
    checkout_to_project_folder()
    print(f"restart_docker_project: {path}")
    stop_docker_project(path)
    start_docker_project(path)
    print("docker restart successful")
