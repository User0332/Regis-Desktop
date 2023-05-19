import os
import subprocess
import msvcrt
import sys
import shutil

RELEASE_BUILD = True if len(sys.argv > 1) and (sys.argv[0] == "debug") else False

print("installing application")

# TODO: Replace the request below and just clone the whole git repo, and then extract the desired build file

subprocess.call(["git", "clone", "https://raw.githubusercontent.com/User0332/Regis-Desktop"])

path_to_installation = f"build/{'release' if RELEASE_BUILD else 'debug-test'}/latest/Regis Desktop"

os.rename(path_to_installation, "Regis Desktop")
shutil.rmtree("Regis-Desktop") # this is the repo

print("making installation directory")

os.chdir("Regis Desktop")

print("creating cache")
os.mkdir("cache")
print("done creating cache")

print("done installing regis desktop")

print("press any key to continue...")
msvcrt.getch()