"""
common utils
"""

import os
import time

from utils.docker.common import start_docker_project
from utils.docker.django import create_django_project
from utils.nginx.main import create_nginx, create_proxy_nginx
from utils.docker.fastapi import create_fastapi_project
from utils.docker.django import start_django_project

import logging

root_dir = "/var/www/html/"

logger = logging.getLogger(__name__)


def handle_html(path: str, domain: str):
    """
    :param path: project path
    :return: None
    # path = root_dir + "{}/{}".format(user, proj_name)
    # os.system("mkdir -p {}".format(path))
    # os.system("git clone {} {}".format(url, path))
    # # os.system("echo '{}' > {}/index.html".format(f"{proj_name} is working fine", path))
    # os.system("chown -R www-data:www-data {}".format(path))
    # os.system("chmod -R 755 {}".format(path))
    # create_nginx(path=path, domain=domain)

    """
    print(f"handle_html: {path}, {domain}")
    os.system("cp -r {} {}".format(path, root_dir))
    os.system("chown -R www-data:www-data {}".format(root_dir))
    os.system("chmod -R 755 {}".format(root_dir))
    create_nginx(path=root_dir + path.split("/")[-1], domain=domain)


def handle_django(path: str, domain: str, port: int = 8001, runcommand: str = "python manage.py runserver"):
    """
    :param path: project path
    :return: None
    """
    print(f"handle_django: {path}, {domain}, {port}, {runcommand}")
    create_django_project(path, domain, port, runcommand)
    create_proxy_nginx(path=path, domain=domain, port=port)
    # time.sleep(10)
    start_django_project(path=path)


def handle_fastapi(path: str, domain: str, port: int = 8001, runcommand: str = "uvicorn main:app --host"):
    """
    :param path: project path
    :return: None
    """
    print(f"handle_fastapi: {path}, {domain}, {port}, {runcommand}")
    create_fastapi_project(path, domain, port, runcommand)
    print(f"handle_fastapi: {path}, {domain}, {port}, {runcommand} created")
    create_proxy_nginx(path=path, domain=domain, port=port)
    print(f"handle_fastapi: {path}, {domain}, {port}, {runcommand} created proxy")
    # time.sleep(10)
    start_docker_project(path=path)
