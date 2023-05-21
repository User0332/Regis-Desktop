import os
import json
import subprocess
import msvcrt
import sys
import stat
import shutil

EXAMPLE_PROFILE_PATH = r"C:\Users\<username>\AppData\Local\Google\Chrome\User Data\Profile1"

def remove_annoying_file(func, annoying_file: str, exc_info):
	os.chmod(annoying_file, stat.S_IWRITE)
	os.unlink(annoying_file)

def configure():
	print("Configuring application...")
	profile_path = input(f"Enter the Chrome profile path to use with the application (ex. {EXAMPLE_PROFILE_PATH}): ")
	
	with open("installation/config.json", 'r') as f:
		obj = json.load(f)

		obj["profilePath"] = profile_path

	with open("installation/config.json", 'w') as f:
		json.dump(obj, f, indent='\t')

	print("done configuring application")

print("If the installation does not work, please run this installer as an administrator.")

try:
	RELEASE_BUILD = False if (len(sys.argv) > 1 and (sys.argv[1] == "debug")) else True
	CONFIGURE = True if (len(sys.argv) > 1 and (sys.argv[1] == "configure")) else False

	if CONFIGURE:
		os.chdir("Regis Desktop")
		configure()
		sys.exit(0)

	print("installing application...")

	# TODO: Replace the request below and just clone the whole git repo, and then extract the desired build file

	if os.path.exists("Regis Desktop"): shutil.rmtree("Regis Desktop", onerror=remove_annoying_file)

	if os.path.exists("Regis-Desktop"): shutil.rmtree("Regis-Desktop", onerror=remove_annoying_file)

	subprocess.call(["git", "clone", "https://github.com/User0332/Regis-Desktop"])

	path_to_installation = f"build/{'release' if RELEASE_BUILD else 'debug-test'}/latest/Regis Desktop"

	os.rename(f"Regis-Desktop/{path_to_installation}", "Regis Desktop")
	
	shutil.rmtree("Regis-Desktop", onerror=remove_annoying_file) # this is the repo

	os.chdir("Regis Desktop")

	print("done installing application")

	print("creating cache...")
	os.mkdir("cache")
	print("done creating cache")

	print("done installing regis desktop")

	configure()

	print("press any key to continue...")
	msvcrt.getch()
except Exception as e:
	print(f"error: {e}")
	msvcrt.getch()