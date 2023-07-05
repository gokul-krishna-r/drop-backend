import os
from common import *


def generate_docker_compose_file(port, runcommand="python manage.py runserver 0.0.0.0:8000"):
    docker_compose = f"""
version: '3'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:{port}"
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
RUN {build_command}
COPY . /code/
    """
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)


def create_django_project(url, projects_folder="projects", project_name="django_project"):
    clone_project(url, projects_folder, project_name)
    generate_docker_compose_file(8000)
    generate_dockerfile()
