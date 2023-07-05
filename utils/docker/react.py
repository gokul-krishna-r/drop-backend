from common import *

def setup():
    os.system("sudo apt-get update")

def create_react_project(url, projects_folder="projects", project_name="react_project"):
    clone_project(url, projects_folder, project_name)
