import os
import logging

logger = logging.getLogger(__name__)


def checkout_to_project_folder():
    logger.info("checkout_to_project_folder")
    os.chdir("/home/ubuntu/drop-backend")
    logger.info(f"{os.getcwd() = }")


def clone_project(url, projects_folder="projects", project_name="django_project"):
    logger.info(f"clone_project: {url}, {projects_folder}, {project_name}")
    os.system(f"git clone {url} {projects_folder}/{project_name}")
    os.chdir(f"{projects_folder}/{project_name}")
    logger.info(f"cloned successful {os.getcwd() = }")
    checkout_to_project_folder()


def start_docker_project(path):
    logger.info(f"start_docker_project: {path}")
    os.chdir(f"{path}")
    os.system("docker compose up -d --build")
    logger.info("docker build successful")
    checkout_to_project_folder()


def stop_docker_project(path):
    logger.info(f"stop_docker_project: {path}")
    os.chdir(f"{path}")
    os.system("docker compose down")
    logger.info("docker stop successful")
    checkout_to_project_folder()


def pull_project(path):
    logger.info(f"pull_project: {path}")
    stop_docker_project(path)
    os.chdir(f"{path}")
    os.system("git pull")
    logger.info("git pull successful")
    checkout_to_project_folder()
    start_docker_project(path)


def restart_docker_project(path):
    logger.info(f"restart_docker_project: {path}")
    stop_docker_project(path)
    start_docker_project(path)
    logger.info("docker restart successful")
