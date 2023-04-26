import os


def git_pull(path):
    os.system("cd {} && git pull".format(path))
