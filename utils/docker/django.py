import os
from utils.docker.common import checkout_to_project_folder,restart_docker_project
def generate_docker_compose_file(port, runcommand="python manage.py runserver 0.0.0.0:8000"):
    docker_compose = f"""
version: '3'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "{port}:8000"
    volumes:
      - .:/code
    command:  {runcommand}
    """
    with open('docker-compose.yml', 'w') as f:
        f.write(docker_compose)

def generate_dockerfile(build_command="python manage.py makemigrations && python manage.py migrate"):
    dockerfile = f"""
FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN {build_command}
    """
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)


def create_django_project(path, domain, port=8000, runcommand="python manage.py runserver"):
    # if clone:
    #     clone_project(url, projects_folder, project_name)
    os.chdir(f"{path}")
    generate_docker_compose_file(port=port, runcommand=runcommand)
    generate_dockerfile()

def start_django_project(path):
    checkout_to_project_folder()
    print(f"start_docker_project: {path}")
    os.chdir(f"{path}")
    os.system("docker compose up -d --build")
    os.system("docker compose exec web python manage.py makemigrations")
    os.system("docker compose exec web python manage.py migrate")
    restart_docker_project(path)
    print("docker build successful")
    checkout_to_project_folder()
