import os
import subprocess
import msvcrt
import sys
import stat
import shutil

try:
	RELEASE_BUILD = False if (len(sys.argv) > 1 and (sys.argv[1] == "debug")) else True

	print("installing application")

	# TODO: Replace the request below and just clone the whole git repo, and then extract the desired build file

	if os.path.exists("Regis Desktop"): shutil.rmtree("Regis Desktop", ignore_errors=True)

	if os.path.exists("Regis-Desktop"):
		os.chmod("Regis-Desktop", stat.S_IRWXO)
		try: shutil.rmtree("Regis-Desktop")
		except PermissionError:
			print("Please run this installer as administrator!")
			exit(1)


	subprocess.call(["git", "clone", "https://github.com/User0332/Regis-Desktop"])

	path_to_installation = f"build/{'release' if RELEASE_BUILD else 'debug-test'}/latest/Regis Desktop"

	os.rename(f"Regis-Desktop/{path_to_installation}", "Regis Desktop")
	
	os.chmod("Regis-Desktop", stat.S_IRWXO)
	shutil.rmtree("Regis-Desktop", ignore_errors=True) # this is the repo

	print("making installation directory")

	os.chdir("Regis Desktop")

	print("creating cache")
	os.mkdir("cache")
	print("done creating cache")

	print("done installing regis desktop")

	print("press any key to continue...")
	msvcrt.getch()
except Exception as e:
	print(f"error: {e}")
	msvcrt.getch()