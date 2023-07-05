import os


def checkout_to_project_folder():
    parent_directory = os.path.abspath(os.path.join('.', os.pardir))
    grandparent_directory = os.path.abspath(os.path.join(parent_directory, os.pardir))
    os.chdir(grandparent_directory)


def clone_project(url, projects_folder="projects", project_name="django_project"):
    os.system(f"git clone {url} {projects_folder}/{project_name}")
    os.chdir(f"{projects_folder}/{project_name}")


def start_docker_project(path):
    os.chdir(f"{path}")
    os.system("docker compose up -d --build")
    checkout_to_project_folder()


def stop_docker_project(path):
    os.chdir(f"{path}")
    os.system("docker compose down")
    checkout_to_project_folder()


def pull_project(path):
    stop_docker_project(path)
    os.chdir(f"{path}")
    os.system("git pull")
    checkout_to_project_folder()
    start_docker_project(path)


def restart_docker_project(path):
    stop_docker_project(path)
    start_docker_project(path)
