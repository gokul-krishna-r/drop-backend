import os
import sys

root_dir = "/var/www/html/"
nginx_root = "/etc/nginx/sites-enabled"


def create_nginx(path, domain):
    if not os.path.exists(nginx_root + "/{}.conf".format(domain)):
        os.system("touch {}/{}.conf".format(nginx_root, domain))
    with open("{}/{}.conf".format(nginx_root, domain), "w") as f:
        f.write("server {\n")
        f.write("\tserver_name {};\n".format(domain))
        f.write("\tindex index.html index.htm index.nginx-debian.html;\n")
        f.write("\tlocation / {\n")
        f.write("\t\tautoindex on;\n")
        f.write("\t\troot {};\n".format(path))
        f.write("\t\ttry_files $uri $uri/ =404;\n")
        f.write("\t}\n")
        f.write("}\n")

    print("nginx file created at", nginx_root)
    os.system("sudo systemctl reload nginx")


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


if __name__ == "__main__":
    create_project(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
