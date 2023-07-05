import os
import sys
from utils.nginx.main import create_nginx, delete_ngnix
from utils.common import check_project_framework_from_path, handle_html, handle_django
from utils.docker.common import clone_project
import logging

#
root_dir = "/var/www/html/"
nginx_root = "/etc/nginx/sites-enabled"
logger = logging.getLogger(__name__)


# root_dir = "/home/sunith/Documents/projects/next/drop-backend/"
# nginx_root = "/home/sunith/Documents/projects/next/drop-backend/nginx"


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
    os.system("rm -r {}/{}".format(root_dir, proj_name))
    delete_ngnix(domain=domain)
    print(f"delete_project: {user}, {proj_name}, {domain} deleted")


if __name__ == "__main__":
    create_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
