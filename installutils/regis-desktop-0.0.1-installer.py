import uuid
UUID: int = None

import sys

if UUID == None:
	with open(sys.argv[0], 'r') as f:
		code = f.read().splitlines()

		code[1] = f"UUID = {uuid.getnode()}"


	with open(sys.argv[0], 'w') as f:
		f.write(
			'\n'.join(code)
		)
else:
	if UUID != uuid.getnode():
		raise RuntimeError("Application was moved to another device")

import time
import json
import os
try: import pyshortcuts
except ImportError:
	os.system("python -m pip install pyshortcuts")
	import pyshortcuts

from tkinter import filedialog
import tkinter as tk
try: import requests
except ImportError:
	os.system("python -m pip install requests")
	import requests

import webbrowser
import subprocess
import shutil


PY_DOWNLOAD = "https://www.python.org/downloads/"

DEFAULT_CONFIG = {
	"$schema": "../schemas/config-schema.json",
	"profilePath": "None",
	"userWidgets": []
}

STABLE_FILES = (
	"regis-desktop.pyc",
	"locals.pyc",
	"signin.pyc",
	"utils.pyc",
	"is_same_device.py"
	"installation/config.json",
	"installation/planners/default.json",
	"requirements.txt"
)

OTHER_FILES = (
	"assets/del-icon.png",
	"assets/plus-icon.png",
	"assets/regis-icon.ico",
	"assets/regis-icon.icns",
	"assets/regis-icon.png",
	"assets/regis-logo-rectangle.png",
	"schemas/config-schema.json",
	"schemas/planner-schema.json"
)

NUM_FILES = len(STABLE_FILES)+len(OTHER_FILES)

PRINT_REPO_URL = "https://github.com/User0332/Regis-Desktop"
REPO_URL = "https://raw.githubusercontent.com/User0332/Regis-Desktop/master/"

INSTALLING: str = None

root = tk.Tk()
root.title("Regis Desktop Installer")
root.geometry("700x400")

def exit_install():
	if INSTALLING:
		try: shutil.rmtree(INSTALLING)
		except PermissionError: pass

	root.destroy()
	sys.exit(0)

def raise_error(errwin: tk.Toplevel, err: tk.Widget, fail=False):
	err.update_idletasks()

	err.grid(row=0, column=0, columnspan=3)
	
	ok = tk.Button(errwin, text=" Ok ", command=exit_install if fail else errwin.destroy)
	ok.grid(row=1, column=0)

	exitbtn = tk.Button(errwin, text=" Exit Installer ", command=exit_install)
	exitbtn.grid(row=1, column=1)

	errwin.update_idletasks()

	errwin.title("Installer Error")
	errwin.geometry(f"{err.winfo_width()+20}x{err.winfo_height()+ok.winfo_height()+2}")
	
	errwin.grab_set()
	errwin.wait_window()
	
def raise_err_str(err: str, fail=False):
	master = tk.Toplevel(root)

	label = tk.Label(master, text=err)

	raise_error(master, label, fail)

def validate_python(): # TODO: print errors to user on tkinter window
	try: ver = subprocess.check_output(["python", "-V"]).decode().removeprefix("Python ")
	except (OSError, subprocess.CalledProcessError):
		master = tk.Toplevel(root)
		wrapper = tk.Frame(master)

		label = tk.Label(wrapper, text="Python isn't installed. Regis Desktop requires Python to run. Get the latest version here: ")
		label.grid(row=0, column=0)

		btn = tk.Button(wrapper, text=PY_DOWNLOAD, command=lambda: webbrowser.open(PY_DOWNLOAD))
		btn.grid(row=0, column=1)

		directions = tk.Label(wrapper, text="Click 'Ok' once Python is installed")
		directions.grid(row=1, column=0)

		raise_error(master, wrapper)

		return validate_python()

	if (not ver.startswith("3.1")) or ver.startswith("3.1."):	
		master = tk.Toplevel(root)
		wrapper = tk.Frame(master)

		label = tk.Label(wrapper, text="An old version of Python is installed. Regis Desktop requires Python version 3.10 or newer to run. Get the latest version here: ")
		label.grid(row=0, column=0)

		btn = tk.Button(wrapper, text=PY_DOWNLOAD, command=lambda: webbrowser.open(PY_DOWNLOAD))
		btn.grid(row=0, column=1)

		directions = tk.Label(wrapper, text="Click 'Ok' once Python is installed")
		directions.grid(row=1, column=0)

		raise_error(master, wrapper)

		return validate_python()
	
def chg_filesvar(var: tk.StringVar, val: int):
	pre, suff = f"Fetching from {PRINT_REPO_URL}: ", f"/{NUM_FILES} Files"

	var.set(
		pre + str(val) + suff
	)

def pack_leave():
	leave = tk.Button(root, text=" Exit Installer ", command=exit_install)
	leave.pack()

	return leave

def configure():
	configure_box = tk.Frame(root)

	title = tk.Label(configure_box, font=("Segoe UI", 15), text="Please enter the Chrome Profile that you use to login to the Intranet")
	title.grid(row=0, column=0)

	label2 = tk.Label(configure_box, text="Chrome Profile Path:")
	label2.grid(row=1, column=0, columnspan=3)

	profilevar = tk.StringVar(configure_box, value="")

	profile_path = tk.Entry(configure_box, textvariable=profilevar)
	profile_path.grid(row=1, column=1)

	how = tk.Label(
		configure_box,
		text=" To get your Chrome Profile Path, open Chrome in the profile that you use to login to the Intranet and go to chrome://version. Copy the filepath next to 'Profile Path' "
	)
	how.grid(row=2, column=0, columnspan=5)

	btnbox = tk.Frame(configure_box)

	okbtn = tk.Button(btnbox, text=" Ok ", command=configure_box.destroy)
	okbtn.grid(row=0, column=0, padx=10)

	leave = tk.Button(btnbox, text=" Exit Installer ", command=exit_install)
	leave.grid(row=0, column=1)

	btnbox.grid(row=3, column=0, columnspan=2)

	configure_box.pack()

	configure_box.wait_window()

	path = profilevar.get()
	
	with open("installation/config.json", 'r') as f:
		try: config = json.load(f)
		except json.decoder.JSONDecodeError: config = DEFAULT_CONFIG

	config["profilePath"] = path

	with open("installation/config.json", 'w') as f:
		json.dump(config, f, indent=4)

def install():
	global INSTALLING
	# TODO: search for exisiting installation

	try: validate_python()
	except RecursionError: exit_install()

	defaultdir = ("C:\\Program Files\\Regis Desktop" if os.name == "nt" else "/Regis")

	store_dir = tk.StringVar(value="Install Directory: "+defaultdir)

	filebox = tk.Frame(root)
	
	installdirlabel = tk.Label(filebox, textvariable=store_dir)
	installdirlabel.grid(row=0, column=0)

	changebutton = tk.Button(
		filebox,
		text=" Change Location ",
		command=lambda: store_dir.set(f"Install Directory: {filedialog.askdirectory(initialdir=store_dir.get().removeprefix('Install Directory: ')) or defaultdir}")
	)
	
	changebutton.grid(row=0, column=1)

	ok = tk.Button(filebox, text=" Ok ", command=filebox.destroy)
	ok.grid(row=1, column=0)

	filebox.pack()
	filebox.wait_window()

	directory = store_dir.get().removeprefix("Install Directory: ")

	try:
		if not os.path.exists(directory): os.mkdir(directory)
	except PermissionError: raise_err_str("Please run the installer as administrator!", fail=True)

	inner = f"{directory}/Regis Desktop Installation"

	INSTALLING = inner

	if os.path.exists(inner): shutil.rmtree(inner)
	os.mkdir(inner)
	os.chdir(inner)

	os.mkdir("cache")
	os.mkdir("assets")
	os.mkdir("schemas")
	os.mkdir("installation")

	complete = tk.StringVar(value=f"Fetching from {PRINT_REPO_URL}: 0/{NUM_FILES} Files")
	fetching = tk.StringVar(value="Fetching: None")

	files_complete = 0

	download_label = tk.Label(root, textvariable=complete)
	download_label.pack()

	fetch_label = tk.Label(root, textvariable=fetching)
	fetch_label.pack()

	leave = pack_leave()
	
	for file in STABLE_FILES:
		fetching.set(f"Fetching: stable/{file}")

		text = requests.get(f"{REPO_URL}/stable/{file}").content
		
		with open(file, "wb") as f:
			f.write(text)

		files_complete+=1
		chg_filesvar(complete, files_complete)

		root.update()

	for file in OTHER_FILES:
		fetching.set(f"Fetching: {file}")

		text = requests.get(f"{REPO_URL}/{file}").content
		
		with open(file, "wb") as f:
			f.write(text)

		files_complete+=1
		chg_filesvar(complete, files_complete)

		root.update()

	fetching.set("Fetching: None")
	leave.destroy()

	deps = tk.Label(root, text="Installing dependencies...")
	deps.pack()

	output = tk.StringVar(value="")

	pipoutput = tk.Label(root, textvariable=output)

	details = tk.Button(root, text=" View details ", command=lambda: pipoutput.pack() if not pipoutput.winfo_ismapped() else None)
	details.pack()

	pip = subprocess.Popen(["python", "-m", "pip", "install", "-r", "requirements.txt"], stdout=subprocess.PIPE)

	while 1:
		byte = pip.stdout.read(1).decode()
		
		if not byte: break # don't use pip.poll() in case user wants to see all details

		output.set(
			(output.get()+byte)[-3200:]
		)

		root.update()

	time.sleep(1) # allow user to read details

	details.destroy()
	pipoutput.destroy()

	shortcut = tk.Label(root, text="Creating shortcut...")
	shortcut.pack()

	leave = pack_leave()

	pyshortcuts.make_shortcut(
		script="regis-desktop.pyc",
		name="Regis Desktop",
		description="Regis Desktop Launcher Shortcut",
		icon=("assets/regis-icon.ico" if os.name == "nt" else "assets/regis-icon.icns"),
		working_dir=inner,
		terminal=False
	)

	leave.destroy()

	done = tk.Label(root, text="Done Installing!")
	done.pack()

	root.update()

	time.sleep(1)

	for child in root.winfo_children(): # clear root
		child.destroy()

	configure()

	INSTALLING = None

	alldone = tk.Label(root, text="All Done!")
	alldone.pack()

	launch = tk.Button(root, text=" Launch Regis Desktop ", command=lambda: (root.after(10, exit_install), subprocess.call(["python", "regis-desktop.pyc"])))
	launch.pack()

	leave = pack_leave()

MAIN_CALLBACK_ID = root.after(10, install)
root.mainloop()