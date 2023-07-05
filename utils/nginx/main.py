import os
import logging
nginx_root = "/etc/nginx/sites-enabled"
logger = logging.getLogger(__name__)


def create_nginx(path, domain):
    logger.info(f"create_nginx: {path}, {domain}")
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


def create_proxy_nginx(path, domain, port):
    logger.info(f"create_proxy_nginx: {path}, {domain}, {port}")
    nginx_root = "/etc/nginx/conf.d"  # Update the nginx_root path if necessary

    if not os.path.exists(f"{nginx_root}/{domain}.conf"):
        os.system(f"touch {nginx_root}/{domain}.conf")

    with open(f"{nginx_root}/{domain}.conf", "w") as f:
        f.write("server {\n")
        f.write("\tserver_name {};\n".format(domain))
        f.write("\tindex index.html index.htm index.nginx-debian.html;\n")
        f.write("\tlocation / {\n")
        f.write("\t\tproxy_set_header X-Real-IP $remote_addr;\n")
        f.write("\t\tproxy_set_header X-Forwarded-For $remote_addr;\n")
        f.write("\t\tproxy_set_header X-Client-Verify SUCCESS;\n")
        f.write("\t\tproxy_set_header Host $http_host;\n")
        f.write("\t\tproxy_set_header X-NginX-Proxy true;\n")
        f.write("\t\tproxy_http_version 1.1;\n")
        f.write("\t\tproxy_set_header Upgrade $http_upgrade;\n")
        f.write("\t\tproxy_set_header Connection \"upgrade\";\n")
        f.write("\t\tproxy_pass http://localhost:{};\n".format(port))
        f.write("\t\tproxy_redirect off;\n")
        f.write("\t\tproxy_buffering off;\n")
        f.write("\t}\n")
        f.write("}\n")

    print("nginx file created at", nginx_root)
    os.system("sudo systemctl reload nginx")


def delete_ngnix(domain):
    logger.info(f"delete_ngnix: {domain}")
    if os.path.exists(nginx_root + "/{}.conf".format(domain)):
        os.system("rm {}/{}.conf".format(nginx_root, domain))
        print("nginx file deleted at", nginx_root)
        os.system("sudo systemctl reload nginx")
