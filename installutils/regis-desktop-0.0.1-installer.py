import pyshortcuts
from tkinter import filedialog
import tkinter as tk
import tkinter.ttk as ttk
import requests
import webbrowser
import subprocess
import shutil
import sys
import os

PY_DOWNLOAD = "https://www.python.org/downloads/"


STABLE_FILES = (
	"regis-desktop.pyc",
	"locals.pyc",
	"signin.pyc",
	"utils.pyc",
	"installation/config.json",
	"requirements.txt"
)

OTHER_FILES = (
	"assets/del-icon.png",
	"assets/plus-icon.png",
	"assets/regis-icon.ico",
	"assets/regis-icon.icns",
	"assets/regis-icon.png",
	"assets/regis-logo-rectangle.png",
	"schemas/config-schema.json"
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

def main():
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
	fetching = tk.StringVar(value="None")

	files_complete = 0

	download_label = tk.Label(root, textvariable=complete)
	download_label.pack()

	fetch_label = tk.Label(root, textvariable=fetching)
	fetch_label.pack()

	leave = pack_leave()
	
	for file in STABLE_FILES:
		fetching.set(f"stable/{file}")

		text = requests.get(f"{REPO_URL}/stable/{file}").content
		
		with open(file, "wb") as f:
			f.write(text)

		files_complete+=1
		chg_filesvar(complete, files_complete)

		root.update()

	for file in OTHER_FILES:
		fetching.set(file)

		text = requests.get(f"{REPO_URL}/{file}").content
		
		with open(file, "wb") as f:
			f.write(text)

		files_complete+=1
		chg_filesvar(complete, files_complete)

		root.update()

	fetching.set("None")
	leave.destroy()

	deps = tk.Label(root, text="Installing dependencies...")
	deps.pack()

	output = tk.StringVar(value="")

	pipoutput = tk.Label(root, textvariable=output)

	details = tk.Button(root, text=" View details ", command=lambda: pipoutput.pack() if not pipoutput.winfo_ismapped() else None)
	details.pack()

	pip = subprocess.Popen(["python", "-m", "pip" "install", "requirements.txt"], stdout=subprocess.PIPE)

	while 1:
		try: output.set(output.get()+pip.stdout.read(1))
		except EOFError: break

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
	
	INSTALLING = None

	alldone = tk.Label(root, text="All Done!")
	alldone.pack()

	launch = tk.Button(root, text=" Launch Regis Desktop ", command=lambda: (root.after(10, exit_install), subprocess.call(["python", "regis-desktop.pyc"])))
	launch.pack()

	leave = pack_leave()

MAIN_CALLBACK_ID = root.after(10, main)
root.mainloop()