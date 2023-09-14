import uuid
import os

x, y, r, t = "12", ''.join((chr(76), chr(54), chr(52), chr(80))), "144", "ab9dn"

pwd = y+y+"102mmd"+x+r+t

def init():
	if not os.path.exists(f"is-same-device:{pwd}"):
		raise FileNotFoundError("Necessary program files were not found")

	with open(f"is-same-device:{pwd}", 'r') as f:
		contents = f.read()

		if not contents: return True

		if contents != str(uuid.getnode()):
			raise RuntimeError("Application moved to unknown device")

	return False

if init():
	with open(f"is-same-device:{pwd}", 'w') as f:
		f.write(str(uuid.getnode()))
