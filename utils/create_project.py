import os
import sys
from nginx.main import create_nginx, delete_ngnix

#
root_dir = "/var/www/html/"
nginx_root = "/etc/nginx/sites-enabled"


# root_dir = "/home/sunith/Documents/projects/next/drop-backend/"
# nginx_root = "/home/sunith/Documents/projects/next/drop-backend/nginx"


def create_project(url, user, proj_name, domain):
    """
    :param url: git url
    :param user: username
    :param proj_name: project name
    :param domain: domain name
    :return: None

    """
    path = root_dir + "{}/{}".format(user, proj_name)
    os.system("mkdir -p {}".format(path))
    os.system("git clone {} {}".format(url, path))
    # os.system("echo '{}' > {}/index.html".format(f"{proj_name} is working fine", path))
    os.system("chown -R www-data:www-data {}".format(path))
    os.system("chmod -R 755 {}".format(path))
    create_nginx(path=path, domain=domain)


def delete_project(user, proj_name, domain):
    path = root_dir + "{}/{}".format(user, proj_name)
    os.system("rm -r {}".format(path))
    delete_ngnix(domain=domain)


if __name__ == "__main__":
    create_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
