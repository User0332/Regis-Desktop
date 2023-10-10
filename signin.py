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
	options = webdriver.ChromeOptions()
	options.add_argument(f"--user-data-dir={locals.SELF_PATH}/regis-data/")
	options.add_argument(f"--profile-directory=Default")

	headless = webdriver.ChromeOptions()
	headless.add_argument(f"--user-data-dir={locals.SELF_PATH}/regis-data/")
	headless.add_argument(f"--profile-directory=Default")
	headless.add_argument("--no-sandbox")
	headless.add_argument("--headless")
	headless.add_argument("--disable-gpu")

	moodleopt = webdriver.ChromeOptions()
	moodleopt.add_argument(f"--user-data-dir={locals.SELF_PATH}/moodle-data/")
	moodleopt.add_argument(f"--profile-directory=Default")	

	signinbrowser = webdriver.Chrome(options=options, service=chrome_service)
	regis = webdriver.Chrome(options=headless, service=chrome_service)
	regisaux = webdriver.Chrome(options=headless, service=chrome_service)


	signin(
		signinbrowser,
		"https://intranet.regis.org/login/MS_SignIn.cfm",
		("https://intranet.regis.org/myRegis/", "https://intranet.regis.org/myRegis/index.cfm"),
		"Regis Intranet"
	)
	
	signinbrowser.close()

	signin(
		regis,
		"https://intranet.regis.org/login/MS_SignIn.cfm",
		("https://intranet.regis.org/myRegis/", "https://intranet.regis.org/myRegis/index.cfm"),
		"Regis Intranet"
	)

	signin(
		regisaux,
		"https://intranet.regis.org/myRegis",
		("https://intranet.regis.org/myRegis/", "https://intranet.regis.org/myRegis/index.cfm"),
		"Regis Intranet"
	)

	moodle = webdriver.Chrome(options=moodleopt, service=chrome_service)

	signin(
		moodle,
		"https://moodle.regis.org/login/index.php",
		("https://moodle.regis.org/my/",),
		"Dashboard"
	)

	moodle.minimize_window()

	regis.get("https://intranet.regis.org/")

	return regis, moodle, regisaux

def signin(driver: webdriver.Chrome, signin_page: str, homepages: tuple[str], homepage_title: str, headless: bool=False):
	if headless:
		try:
			driver.get(homepages[0])

			if (driver.current_url not in homepages) or (driver.title != homepage_title): raise InvalidArgumentException()
		except InvalidArgumentException:
			print(f"ERR: You are not signed in to '{homepages[0]}' ({homepage_title})!")
			exit(1)

		return
	
	driver.get(signin_page)

	while (
		(driver.current_url not in homepages)
	): pass
	