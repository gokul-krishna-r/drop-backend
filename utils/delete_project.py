import os
import sys

#
root_dir = "/var/www/html/"
nginx_root = "/etc/nginx/sites-enabled"


# root_dir = "/home/sunith/Documents/projects/next/drop-backend/"
# nginx_root = "/home/sunith/Documents/projects/next/drop-backend/nginx"


def delete_ngnix(domain):
    if os.path.exists(nginx_root + "/{}.conf".format(domain)):
        os.system("rm {}/{}.conf".format(nginx_root, domain))
        print("nginx file deleted at", nginx_root)
        os.system("sudo systemctl reload nginx")

def delete_project(user,proj_name,domain):
    path = root_dir + "{}/{}".format(user, proj_name)
    os.system("rm -rf {}".format(path))
    delete_ngnix(domain=domain) 

if __name__ == "__main__":
    delete_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
