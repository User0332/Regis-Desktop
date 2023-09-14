import subprocess
import os

x, y, r, t = "12", ''.join((chr(76), chr(54), chr(52), chr(80))), "144", "ab9dn"

pwd = y+y+"102mmd"+x+r+t

def get_uuid():
	if os.name == "nt": return subprocess.check_output(
		["wmic", "csproduct", "get", "uuid"]
	).decode().splitlines()[1]
		
	## only other platform this will be running on is macos

	return subprocess.check_output(
		"ioreg -d2 -c IOPlatformExpertDevice | awk -F\\\" '/IOPlatformUUID/{print $(NF-1)}'",
		shell=True
	)

def init():
	if not os.path.exists(f"is-same-device:{pwd}"):
		raise FileNotFoundError("Necessary program files were not found")

	with open(f"is-same-device:{pwd}", 'r') as f:
		contents = f.read()

		if not contents: return True

		if contents != get_uuid():
			raise RuntimeError("Application moved to unknown device")

	return False

if init():
	with open(f"is-same-device:{pwd}", 'w') as f:
		f.write(get_uuid())
