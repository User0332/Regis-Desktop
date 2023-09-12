import os
import locals
import time
from sys import exit, platform as sys_platform
if sys_platform == "win32": from subprocess import CREATE_NO_WINDOW
else: CREATE_NO_WINDOW = 0 # figure how to emulate on linux + mac
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common import InvalidArgumentException

chrome_service = Service()
chrome_service.creation_flags = CREATE_NO_WINDOW

def makebrowsers(path: str) -> tuple[webdriver.Chrome, webdriver.Chrome, webdriver.Chrome]:
	split = os.path.normpath(path).split('\\')
	pathdir = '\\'.join(split[:-1])
	profile = split[-1]
	
	options = webdriver.ChromeOptions()
	options.add_argument(f"--user-data-dir={locals.SELF_PATH}/user-data/")
	options.add_argument(f"--profile-directory=Default")
	# options.add_argument("--no-sandbox")
	# options.add_argument("--headless")
	# options.add_argument("--disable-gpu")

	headless = webdriver.ChromeOptions()
	headless.add_argument(f"--user-data-dir={locals.SELF_PATH}/user-data/")
	headless.add_argument(f"--profile-directory=Default")
	headless.add_argument("--no-sandbox")
	headless.add_argument("--headless")
	headless.add_argument("--disable-gpu")

	regis = webdriver.Chrome(options=options, service=chrome_service)

	signin(
		regis,
		"https://intranet.regis.org/login/MS_SignIn.cfm",
		"https://intranet.regis.org/myRegis/",
		"Regis Intranet"
	)

	regis.minimize_window()

	regisaux = webdriver.Chrome(options=headless, service=chrome_service)

	signin(
		regisaux,
		"https://intranet.regis.org/login/MS_SignIn.cfm",
		"https://intranet.regis.org/myRegis/",
		"Regis Intranet",
	)

	regisaux.minimize_window()

	moodle = webdriver.Chrome(service=chrome_service)

	signin(
		moodle,
		"https://moodle.regis.org/login/index.php",
		"https://moodle.regis.org/my/",
		"Dashboard"
	)

	moodle.minimize_window()

	regis.get("https://intranet.regis.org/")

	return regis, moodle, regisaux

def signin(driver: webdriver.Chrome, signin_page: str, homepage: str, homepage_title: str, headless: bool=False):
	if headless:
		try:
			driver.get(signin_page)

			time.sleep(1)

			print(driver.current_url)
			print(driver.find_element(By.CSS_SELECTOR, "#lightbox > div:nth-child(2) > img"))


			if (driver.current_url != homepage) or (driver.title != homepage_title): raise InvalidArgumentException()
		except InvalidArgumentException:
			print(f"ERR: You are not signed in to '{homepage}' ({homepage_title})!")
			exit(1)

		return
	
	driver.get(signin_page)

	while (
		(driver.current_url != homepage) and 
		(driver.title != homepage_title)
	): pass
	