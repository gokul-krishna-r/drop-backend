# like django.py generate required files for fastapi

# Path: utils/docker/fastapi.py
# Compare this snippet from utils/docker/django.py:


import os


def generate_docker_compose_file(port, runcommand="uvicorn main:app --reload"):
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


def generate_dockerfile(build_command="pip install -r requirements.txt"):
    dockerfile = f"""
FROM python:3.9
    
ENV PYTHONUNBUFFERED 1
    
RUN mkdir /code
WORKDIR /code
    
COPY requirements.txt /code/
RUN {build_command}
COPY . /code/
    """
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile)


def create_fastapi_project(path, domain, port=8000, runcommand="uvicorn main:app --reload"):
    os.chdir(f"{path}")
    generate_docker_compose_file(port=port, runcommand=runcommand)
    generate_dockerfile()
