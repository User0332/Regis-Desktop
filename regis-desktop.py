from contextlib import redirect_stdout
from promiseapi import PromiseFuncWrap
from typing import Callable
from domapi import make_document_from_str, Document, Element
from locals import *
from sys import exit
import secrets
import time
import string
import utils
import locals
import signin

with redirect_stdout(open("nul",'w')): import pygame

CONFIG = utils.load_config()

utils.load_nonvolatile_cache()

regis, moodle, regisauxpage = signin.makebrowsers(CONFIG["profilePath"])

BUTTON_HANDLERS: dict[str, dict[str, pygame.Rect | Callable[[dict[str]], None] | pygame.Surface | dict[str]]] = {}

def chgauxpage(page: str):
	if regisauxpage.current_url != page: PromiseFuncWrap(lambda: regisauxpage.get(page))

def boilerpage(home=False, from_sched=False):
	screen.fill(
		DEFAULT_SCREEN_BACKGROUND_COLOR
	)
	screen.blit(logo_box, logo_rect())

	if home: return
	if from_sched:
		make_button("Back to Schedule", lambda: changepage("schedule"), (size()[0]-200, 5), "back-btn")
		return

	make_button("Back to Home", lambda: changepage("homescreen"), (size()[0]-150, 5), "back-btn")

def build_lunch():
	boilerpage(from_sched=True)

	chgauxpage("https://intranet.regis.org/dining/")
	
	width, height = size()
	document = make_document_from_str(
		utils.cache_get_src(regisauxpage, "https://intranet.regis.org/dining/")
	)

	sections = document.querySelector(".panel-primary").lastElementChild.children
	sections_dict = {
		section.firstElementChild.textContent: [
			' '.join(
				section.textContent
				.replace('\n', '')
				.replace("       ", '')
				.split()[1:]
			)
		]
		for section in sections
	}

	for i, section in enumerate(sections_dict):
		pos = ((i*200)+5, 100)
		if i % 2: pos = (((i-1)*200)+5, 320)

		if i == len(sections_dict)-1: pos = (5, 540)

		build_list_box(
			sections_dict[section],
			section,
			pos,
			600
		)

	if locals.SCROLL_OFFSET > -150:
		text = get_default_text("Scroll down for Lunchtime Events", background=NOTICE_COLOR)

		screen.blit(
			text,
			(width-text.get_size()[0]-5, height-30)
		)

	document = make_document_from_str(
		utils.cache_get_src(regis)
	)
	
	events_parent = document.querySelector("#myprimarykey_44 > div > div > div.row > div > div > div.panel-body > table > tbody")
	if events_parent: events_list = [
		event for event in [
			f"{child.firstElementChild.firstElementChild.textContent.strip()} ({child.lastElementChild.textContent.strip()})"
			for child in events_parent.children
		] if ("12:00 PM -" in event)
	]
	else: events_list = ["No Community Events Today :("]

	build_list_box(
		events_list,
		"Lunchtime Events",
		(5, 700),
		width
	)

	lunch_balance = document.querySelector("body > div > div > div.col-md-3 > div > div > div:nth-child(7) > div > a").textContent

	screen.blit(
		get_default_text(f"Lunch Balance: {lunch_balance}"),
		(width/2, 700)
	)

def build_comm_time_events():
	document = make_document_from_str(
		utils.cache_get_src(regis)
	)

	boilerpage(from_sched=True)

	events_parent = document.querySelector("#myprimarykey_44 > div > div > div.row > div > div > div.panel-body > table > tbody")
	if events_parent: events_list = [
		event for event in [
			f"{child.firstElementChild.firstElementChild.textContent.strip()} ({child.lastElementChild.textContent.strip()})"
			for child in events_parent.children
		] if ("10:30 AM -" in event)
	]
	else: events_list = ["No Community Events Today :("]

	build_list_box(
		events_list,
		"Community Time Events",
		(5, 100),
		size()[0]*2
	)
	
	text = get_default_text("More non-community time events are located on the homepage", background=NOTICE_COLOR)


	screen.blit(
		text,
		(size()[0]-text.get_size()[0]-5, size()[1]-30)
	)

def build_schedule():
	boilerpage()

	document = make_document_from_str(
		utils.cache_get_src(regis)
	)

	make_schedule_box(document, (5, 100))

def build_assignments():
	boilerpage()

	document = make_document_from_str(
		utils.cache_get_src(regis)
	)
	moodle_document = make_document_from_str(
		utils.cache_get_src(moodle, "https://moodle.regis.org/my/", milliseconds=70), 
	)

	tests_div = document.querySelector("#myprimarykey_34 > div > div")
	tests = [test.textContent.strip().replace("\n\n \n", " - ").replace("     \n\n     - ", ", ") for test in tests_div.children[1:]]

	assns_div = moodle_document.querySelector("#inst21750 > div > div > div > div")
	assns = [child.querySelector('a').textContent+f" ({child.querySelector('div.date').textContent})" for child in assns_div.children[1:]]

	width = size()[0]

	build_list_box(tests, "Upcoming Tests", (5, 100), width-(width/6.5))
	build_list_box(assns, "Upcoming Assignments", (600, 100), width-width/10)

def build_homescreen():
	boilerpage(home=True)

	document = make_document_from_str(
		utils.cache_get_src(regis)
	)

	firstname = document.querySelector("body > nav > div > div.navbar-header > div > span:nth-child(1)").textContent.split()[0]

	largefont = pygame.font.SysFont("Helvetica", 30, bold=True)

	screen.blit(
		largefont.render(f"Welcome, {firstname}! Here's what's happening today:", True, "black"),
		(10, 75+locals.SCROLL_OFFSET)
	)

	make_button("Assignments :)", lambda: changepage("assignments"), (5, 380), "see-assns")
	make_button("Schedule :)", lambda: changepage("schedule"), (5, 410), "see-schedule")

	letter_day = get_letter_day(document.querySelector("#myprimarykey_43 > div > div > div:nth-child(4)"))

	if letter_day == "not a school/letter":
		screen.blit(
			largefont.render("Today isn't a school/letter day!", True, "black"),
			(10, 130+locals.SCROLL_OFFSET)
		)
		
		return

	normal_classes, late_classes = utils.get_current_and_next_class(
		document.querySelector("#myprimarykey_43 > div > div > div:nth-child(6)").children[string.ascii_uppercase.index(letter_day)+1]
	)

	screen.blit(
		largefont.render("Normal Timing", True, "black"),
		(10, 130+locals.SCROLL_OFFSET)
	)

	screen.blit(
		largefont.render("Late Start Timing", True, "black"),
		(10, 250+locals.SCROLL_OFFSET)
	)

	screen.blit(
		get_default_text(f"Current Mod: {normal_classes[0]}", "black"),
		(10, 170+locals.SCROLL_OFFSET)
	)

	screen.blit(
		get_default_text(f"Next Mod: {normal_classes[1]}", "black"),
		(10, 200+locals.SCROLL_OFFSET)
	)

	screen.blit(
		get_default_text(f"Current Mod: {late_classes[0]}", "black"),
		(10, 290+locals.SCROLL_OFFSET)
	)

	screen.blit(
		get_default_text(f"Next Mod: {late_classes[1]}", "black"),
		(10, 320+locals.SCROLL_OFFSET)
	)

	# TODO: add events next to the current/next mod section


	events_parent = document.querySelector("#myprimarykey_44 > div > div > div.row > div > div > div.panel-body > table > tbody")
	if events_parent: events_list = [
		f"{child.firstElementChild.firstElementChild.textContent.strip()} ({child.lastElementChild.textContent.strip()})"
		for child in events_parent.children
	]
	else: events_list = ["No Community Events Today :("]

	build_list_box(
		events_list,
		"Today's Events",
		(700, 75),
		size()[0]*(3/4)
	)

def build_list_box(_list: list, title: str, pos: tuple[int, int], maxwidth: int, color_cycle: tuple[pygame.Color]=("black",), background_color_cycle: tuple[pygame.Color]=(None,), buttonize: dict={}):
	lines, line_parent_map = utils.wrap_text(_list, int(maxwidth/font.size('m')[0]))

	screen.blit(
		get_default_text(title, "white", background=DEFAULT_TEXT_BACKGROUND_COLOR),
		(pos[0], pos[1]+locals.SCROLL_OFFSET)
	)

	for i, line in enumerate(lines):
		parent_lineno = line_parent_map[i]

		if parent_lineno in buttonize.keys():
			make_button(
				line, buttonize[parent_lineno],
				(pos[0], (i*30)+50+pos[1]),
				f"buttonized-{secrets.token_urlsafe(5)}",
				color=color_cycle[parent_lineno%len(color_cycle)],
				background_color=background_color_cycle[parent_lineno%len(background_color_cycle)]
			)

			continue

		screen.blit(
			get_default_text(line, color=color_cycle[parent_lineno%len(color_cycle)], background=background_color_cycle[parent_lineno%len(background_color_cycle)]),
			(pos[0], (i*30)+50+pos[1]+locals.SCROLL_OFFSET)
		)

def get_letter_day(parent_div: Element) -> str:
	for child in parent_div.children:
		if "background-color:#69ba2c;" in child.firstElementChild.getAttribute("style"):
			return child.firstElementChild.firstElementChild.textContent
		
	return "not a school/letter"

def make_schedule_box(document: Document, pos: tuple[int, int]):
	letter_day = get_letter_day(document.querySelector("#myprimarykey_43 > div > div > div:nth-child(4)"))

	width = size()[0]

	screen.blit(
		get_default_text(f"Today is {letter_day} day!", "black"),
		(pos[0], pos[1]+locals.SCROLL_OFFSET)
	)

	if letter_day == "not a school/letter": return

	# make a column for today and tmrw schedule AND events
	schedule_elements = document.querySelector("#myprimarykey_43 > div > div > div:nth-child(6)").children
	
	today_div = schedule_elements[string.ascii_uppercase.index(letter_day)+1]
	try: tmrw_div = schedule_elements[string.ascii_uppercase.index(letter_day)+2]
	except IndexError: tmrw_div = schedule_elements[1]

	todays_schedule = utils.parse_schedule(today_div)
	tomorrows_schedule = utils.parse_schedule(tmrw_div)

	buttonize = {
		todays_schedule.index("Lunch"): lambda: changepage("lunch")
	}

	if "Community Time" in todays_schedule:
		buttonize[todays_schedule.index("Community Time")] = lambda: changepage("comm_time_events")

	build_list_box(
		todays_schedule,
		"Today's Classes",
		(pos[0], pos[1]+30),
		width*(3/4),
		background_color_cycle=utils.get_schedule_colors(today_div),
		buttonize=buttonize
	)

	build_list_box(
		tomorrows_schedule,
		"Next School Day's Classes",
		(pos[0]+width/2, pos[1]+30),
		width*(3/4),
		background_color_cycle=utils.get_schedule_colors(tmrw_div)
	)
	
def get_default_text(text: str, color: pygame.Color="black", background: pygame.Color=None):
	return font.render(f" {text} ", True, color, background) # f" {text} " for background padding

def default_button_hover(values: dict[str, ]):
	values["background_color"] = BUTTON_HOVER_COLOR

def default_button_update(values: dict[str]):
	values.pop("background_color") # let the next call decide the color

def make_button(text: str, action: Callable[[], None], pos: tuple[int, int], _id: str, hover: Callable[[dict[str]], None]=default_button_hover, update: Callable[[dict[str]], None]=default_button_update, color: pygame.Color="white", background_color: pygame.Color="red"):
	size = font.size(text)
	button = pygame.Surface((size[0]+20, size[1]+2))
	button.fill(DEFAULT_SCREEN_BACKGROUND_COLOR)

	if BUTTON_HANDLERS.get(_id):
		values = BUTTON_HANDLERS[_id]["values"]

		text, color, background_color = values.get("text", text), values.get("color", color), values.get("background_color", background_color)
		action = BUTTON_HANDLERS[_id]["handler"]
		hover = BUTTON_HANDLERS[_id]["hover"]
		update = BUTTON_HANDLERS[_id]["update"]

	text_surf = get_default_text(text, color)

	# rounded background
	pygame.draw.rect(button, background_color, (0, 0, *button.get_size()), border_radius=7)

	button.blit(text_surf, (5, 0))

	text_rect = button.get_rect(topleft=(pos[0], pos[1]+locals.SCROLL_OFFSET))

	BUTTON_HANDLERS[_id] = {
		"rect": text_rect,
		"handler": action,
		"hover": hover,
		"update": update,
		"values": {
			"text": text,
			"color": color,
			"background_color": background_color
		}
	}

	screen.blit(button, text_rect)

	return button, text_rect

def changepage(page: str):
	BUTTON_HANDLERS.clear() # clear these so the next page can add its own
	locals.page = page

def refresh_page():
	regisaux_not_reloaded = False
	moodle_not_reloaded = False

	while pygame.get_init():
		time.sleep(10)
		regis.refresh()

		if page not in ("lunch",): regisauxpage.refresh()
		elif regisaux_not_reloaded:
			regisauxpage.refresh()
			regisaux_not_reloaded = False
		else: regisaux_not_reloaded = True


		if page not in ("assignments",): moodle.refresh()
		elif moodle_not_reloaded:
			moodle.refresh()
			moodle_not_reloaded = False
		else: moodle_not_reloaded = True

pygame.init()

PromiseFuncWrap(refresh_page) # refresh every 10 secs

info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h-100), pygame.RESIZABLE)
size = screen.get_size

# NOTE: FIGURE OUT HOW TO MOVE PYGAME WINDOW TO TOP

logo_box = pygame.transform.scale(
	pygame.image.load("assets/regis-logo-rectangle.png"),
	(280, 58)
)
logo_rect = lambda: logo_box.get_rect(topleft=(5, 5+locals.SCROLL_OFFSET))

regis_icon = pygame.image.load("assets/regis-icon.png")
pygame.display.set_caption("Regis Intranet Desktop")
pygame.display.set_icon(regis_icon)

font = pygame.font.SysFont("Helvetica", 20, bold=True) # get actual font from site

while 1:
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			if logo_rect().collidepoint(*pygame.mouse.get_pos()): changepage("homescreen")
			# click button
			try:
				for handler in BUTTON_HANDLERS.values():
					if handler["rect"].collidepoint(*pygame.mouse.get_pos()): handler["handler"]()
			except RuntimeError as e:
				if str(e) == "dictionary changed size during iteration": continue # this means the page changed and BUTTON_HANDLERS was cleared
				raise
		if event.type == pygame.MOUSEWHEEL:
			locals.SCROLL_OFFSET = min(max(locals.SCROLL_OFFSET+event.y*10, -800), 0)
		if event.type == pygame.QUIT:
			pygame.quit()
			regis.quit()
			regisauxpage.quit()
			moodle.quit()
			utils.write_nonvolatile_cache()
			exit(0)

	# hover effect for buttons
	for handler in BUTTON_HANDLERS.values():
		if handler["rect"].collidepoint(*pygame.mouse.get_pos()): handler["hover"](handler["values"])
		
	globals()[f"build_{locals.page}"]()

	# button update func
	for handler in BUTTON_HANDLERS.values(): handler["update"](handler["values"])

	pygame.display.update()