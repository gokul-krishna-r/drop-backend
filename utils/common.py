"""
common utils
"""

import os
import time

from utils.docker.common import start_docker_project
from utils.docker.django import create_django_project
from utils.nginx.main import create_nginx, create_proxy_nginx
import logging

root_dir = "/var/www/html/"

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
    time.sleep(10)
    start_docker_project(path=path)
