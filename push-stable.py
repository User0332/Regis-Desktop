import py_compile
import subprocess
import shutil
import os
import sys

TEMP = "compiled.temp"

files = sys.argv[1:]

for file in files:
	if file.endswith(".py"):
		subprocess.call(
			[
				"python", "-m",
				"python_minifier", file,
				"--output", TEMP
			]
		)

		py_compile.compile(TEMP, f"stable/{file}c")
	
		continue

	shutil.copy(file, f"stable/{file}")

try: os.remove(TEMP)
except OSError: pass