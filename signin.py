import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import InvalidArgumentException

def makebrowsers(path: str) -> tuple[webdriver.Chrome, webdriver.Chrome, webdriver.Chrome]:
	options = webdriver.ChromeOptions()

	split = os.path.normpath(path).split('\\')
	pathdir = '\\'.join(split[:-1])
	profile = split[-1]

	options.binary_location
	options.add_argument(f"--user-data-dir={pathdir}")
	options.add_argument(f"--profile-directory={profile}")
	options.add_argument("--no-sandbox")
	options.add_argument("--headless")
	options.add_argument("--disable-gpu")

	regis = webdriver.Chrome(options=options)
	regisaux = webdriver.Chrome(options=options)

	signin(
		regis,
		"https://www.regis.org/login.cfm",
		"https://intranet.regis.org/myRegis",
		"myRegis",
		headless=True
	)

	signin(
		regisaux,
		"https://www.regis.org/login.cfm",
		"https://intranet.regis.org/myRegis",
		"myRegis",
		headless=True
	)

	moodle = webdriver.Chrome()

	signin(
		moodle,
		"https://moodle.regis.org/login/index.php",
		"https://moodle.regis.org/my/",
		"Dashboard"
	)

	regis.get("https://intranet.regis.org")

	moodle.minimize_window()

	return regis, moodle, regisaux

def signin(driver: webdriver.Chrome, signin_page: str, homepage: str, homepage_title: str, headless: bool=False):
	if headless:
		try:
			driver.get(homepage)
			if driver.title != homepage_title: raise InvalidArgumentException()
		except InvalidArgumentException:
			print(f"ERR: You are not signed in to '{homepage}'!")
			exit(1)

		return
	
	driver.get(signin_page)

	while (
		(driver.current_url != homepage) and 
		(driver.title != homepage_title)
	): pass
	