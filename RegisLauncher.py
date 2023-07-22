import subprocess
import os
import sys

os.chdir(
    os.path.dirname(sys.argv[0])
)

subprocess.call(["pythonw", "regis-desktop.pyc"])