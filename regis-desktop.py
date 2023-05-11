from contextlib import redirect_stdout
from ctypes import windll
from promiseapi import PromiseFuncWrap
from types import FunctionType
from domapi import make_document_from_str, Document, Element
import datetime
import tinycss
import time
import string
import utils
import locals
import signin

with redirect_stdout(open("nul",'w')): import pygame

regis, moodle = signin.makebrowsers()

BUTTON_HANDLERS: list[dict[str, pygame.Rect | FunctionType | pygame.Surface]] = []
SCHEDULE_COLOR_CYCLE = (
	(3, 252, 132),
	(219, 3, 252),
	(3, 123, 252),
	(204, 89, 51),
	(204, 51, 171),
	(196, 204, 51)
)
DEFAULT_TEXT_BACKGROUND_COLOR = (200, 50, 50)
HEIGHT_PX_15_MIN = 90
BUTTON_HOVER_COLOR = (166, 5, 5)
TIMES = (
	datetime.time(8, 30),
	datetime.time(8, 45),
	datetime.time(9),
	datetime.time(9, 15),
	datetime.time(9, 30),
	datetime.time(9, 45),
	datetime.time(10),
	datetime.time(10, 15),
	datetime.time(10, 30),
	datetime.time(10, 45),
	datetime.time(11),
	datetime.time(11, 15),
	datetime.time(11, 30),
	datetime.time(11, 45),
	datetime.time(12),
	datetime.time(12, 15),
	datetime.time(12, 30),
	datetime.time(12, 45),
	datetime.time(13),
	datetime.time(13, 15),
	datetime.time(13, 30),
	datetime.time(13, 45),
	datetime.time(14),
	datetime.time(14, 15),
	datetime.time(14, 30),
	datetime.time(14, 45),
	datetime.time(15)
)
LATE_TIMES = TIMES[3:]

def boilerpage(home=False):
	BUTTON_HANDLERS.clear() # remove old page handlers, which will be recreated on return
	screen.fill("white")
	screen.blit(logo_box, logo_rect)

	if home: return

	make_button("Back to Home", lambda: changepage("homescreen"), (size()[0]-150, 5))

def build_schedule():
	boilerpage()

	document = make_document_from_str(regis.page_source)

	make_schedule_box(document, (5, 100))

def build_assignments():
	boilerpage()

	document = make_document_from_str(regis.page_source)
	moodle_document = make_document_from_str(moodle.page_source)

	tests_div = document.querySelector("#myprimarykey_34 > div > div")
	tests = [test.textContent.strip().replace("\n\n \n", " - ").replace("     \n\n     - ", ", ") for test in tests_div.children[1:]]

	assns_div = moodle_document.querySelector("#inst21750 > div > div > div > div")
	assns = [child.querySelector('a').textContent+f" ({child.querySelector('div.date').textContent})" for child in assns_div.children[1:]]

	build_list_box(tests, "Upcoming Tests", (5, 100), size()[0]-100)
	build_list_box(assns, "Upcoming Assignments", (600, 100), size()[0])

def build_homescreen():
	boilerpage(home=True)

	document = make_document_from_str(regis.page_source)

	firstname = document.querySelector("body > nav > div > div.navbar-header > div > span:nth-child(1)").textContent.split()[0]

	largefont = pygame.font.SysFont("Helvetica", 30, bold=True)

	screen.blit(
		largefont.render(f"Welcome, {firstname}! Here's what's happening today:", False, "black"),
		(10, 75)
	)

	letter_day = get_letter_day(document.querySelector("#myprimarykey_43 > div > div > div:nth-child(4)"))

	if letter_day == "not a school/letter":
		screen.blit(
			largefont.render("Today isn't a school/letter day!", False, "black"),
			(10, 130)
		)
		
		return

	normal_schedule, late_schedule = schedule_convert_15min(
		document.querySelector("#myprimarykey_43 > div > div > div:nth-child(6)").children[string.ascii_uppercase.index(letter_day)+1]
	)

	curr_time = datetime.datetime.now().time()

	normal_classes = ["No class!", "No class!"]
	late_classes = ["No class!", "No class!"]

	try:
		for i, classtime in enumerate(normal_schedule.keys()):
			if (curr_time < classtime) and (curr_time > tuple(normal_schedule.keys())[i-1]):
				normal_classes = [tuple(normal_schedule.values())[i-1], normal_schedule[classtime]]
				break
	except IndexError: normal_classes[1] = normal_schedule[classtime]

	try:
		for i, classtime in enumerate(late_schedule.keys()):
			if (curr_time < classtime) and (curr_time > tuple(late_schedule.keys())[i-1]):
				late_classes = [tuple(late_schedule.values())[i-1], late_schedule[classtime]]
				break
	except IndexError: late_classes[1] = late_schedule[classtime]

	if (curr_time < datetime.time(15, 15)) and (curr_time > datetime.time(15)):
		normal_classes[0] = tuple(normal_schedule.values())[-1]
		late_classes[0] = tuple(normal_schedule.values())[-1]

	screen.blit(
		largefont.render("Normal Timing", False, "black"),
		(10, 130)
	)

	screen.blit(
		largefont.render("Late Start Timing", False, "black"),
		(10, 250)
	)

	screen.blit(
		get_default_text(f"Current Mod: {normal_classes[0]}", "black"),
		(10, 170)
	)

	screen.blit(
		get_default_text(f"Next Mod: {normal_classes[1]}", "black"),
		(10, 200)
	)

	screen.blit(
		get_default_text(f"Current Mod: {late_classes[0]}", "black"),
		(10, 290)
	)

	screen.blit(
		get_default_text(f"Next Mod: {late_classes[1]}", "black"),
		(10, 320)
	)

	# TODO: add events next to the current/next mod section

	make_button("Assignments :)", lambda: changepage("assignments"), (5, 380))
	make_button("Schedule :)", lambda: changepage("schedule"), (5, 410))

	events_parent = document.querySelector("#myprimarykey_44 > div > div > div.row > div > div > div.panel-body > table > tbody")
	events_list = [
		f"{child.firstElementChild.firstElementChild.textContent.strip()} ({child.lastElementChild.textContent.strip()})"
		for child in events_parent.children
	]

	build_list_box(
		events_list,
		"Today's Events",
		(700, 75),
		size()[0]*(3/4)
	)

def build_list_box(_list: list, title: str, pos: tuple[int, int], maxwidth: int, color_cycle: tuple[tuple[int, int, int]]=("black",), background_color_cycle: tuple[tuple[int, int, int]]=(None,)):
	lines, line_parent_map = utils.wrap_text(_list, int(maxwidth/font.size('m')[0]))

	screen.blit(
		get_default_text(title, "white", background=DEFAULT_TEXT_BACKGROUND_COLOR),
		pos
	)

	for i, line in enumerate(lines):
		parent_lineno = line_parent_map[i]
		screen.blit(
			get_default_text(line, color=color_cycle[parent_lineno%len(color_cycle)], background=background_color_cycle[parent_lineno%len(background_color_cycle)]),
			(pos[0], (i*30)+50+pos[1])
		)

def get_letter_day(parent_div: Element) -> str:
	for child in parent_div.children:
		if "background-color:#69ba2c;" in child.firstElementChild.getAttribute("style"):
			return child.firstElementChild.firstElementChild.textContent
		
	return "not a school/letter"

def schedule_convert_15min(schedule_div: Element) -> tuple[
	dict[datetime.datetime, str],
	dict[datetime.datetime, str]
]:
	classes: list[str] = []

	for child in schedule_div.children:
		declarations: list[tinycss.css21.Declaration] = tinycss.CSS21Parser().parse_style_attr(child.getAttribute("style"))[0]
		for decl in declarations:
			if decl.name == "height":
				height: int = decl.value[0].value

				num_blocks = int(height/HEIGHT_PX_15_MIN)

				classes.extend([child.textContent.strip().replace('\n', ' ')]*num_blocks)
				break

		while "" in classes: classes[classes.index("")] = "Free"

	return (
		{ TIMES[i]: _class for i, _class in enumerate(classes) },
		{ LATE_TIMES[i]: _class for i, _class in enumerate([x for x in classes if x != "Community Time"]) }
	)

def get_schedule_colors(schedule_div: Element) -> tuple[pygame.Color]:
	colors = []

	for child in schedule_div.children:
		declarations: list[tinycss.css21.Declaration] = tinycss.CSS21Parser().parse_style_attr(child.getAttribute("style"))[0]
		if child.textContent.strip() == "":
			colors.append("#fffbed") # free mod color
			continue
		
		for decl in declarations:
			if decl.name == "background-color":
				colors.append(decl.value[0].value)
				break


	return tuple(
		[pygame.Color(color) for i, color in enumerate(colors) if (i == 0) or not (color == "#fffbed" == colors[i-1])]
	)

def make_schedule_box(document: Document, pos: tuple[int, int]):
	letter_day = get_letter_day(document.querySelector("#myprimarykey_43 > div > div > div:nth-child(4)"))

	width = size()[0]

	screen.blit(
		get_default_text(f"Today is {letter_day} day!", "black"),
		(pos[0], pos[1])
	)

	if letter_day == "not a school/letter": return

	# make a column for today and tmrw schedule AND events
	schedule_elements = document.querySelector("#myprimarykey_43 > div > div > div:nth-child(6)").children
	
	today_div = schedule_elements[string.ascii_uppercase.index(letter_day)+1]
	tmrw_div = schedule_elements[string.ascii_uppercase.index(letter_day)+2]

	todays_schedule = utils.parse_schedule(today_div.textContent)
	try: tomorrows_schedule = utils.parse_schedule(tmrw_div.textContent)
	except IndexError: tomorrows_schedule = utils.parse_schedule(schedule_elements[1].textContent)

	build_list_box(
		todays_schedule,
		"Today's Classes",
		(pos[0], pos[1]+30),
		width*(3/4),
		background_color_cycle=get_schedule_colors(today_div)
	)

	build_list_box(
		tomorrows_schedule,
		"Next School Day's Classes",
		(pos[0]+width/2, pos[1]+30),
		width*(3/4),
		background_color_cycle=get_schedule_colors(tmrw_div)
	)
	
def get_default_text(text: str, color: pygame.Color, background: pygame.Color=None):
	return font.render(f" {text} ", False, color, background) # f" {text} " for background padding

def make_button(text: str, action: FunctionType, position: tuple[int, int], color: pygame.Color="red"):
	size = font.size(text)
	button = pygame.Surface((size[0]+20, size[1]+2))
	button.fill("white")

	text_surf = get_default_text(text, "white")

	# rounded background
	pygame.draw.rect(button, color, (0, 0, *button.get_size()), border_radius=7)

	button.blit(text_surf, (5, 0))

	text_rect = button.get_rect(topleft=position)

	BUTTON_HANDLERS.append(
		{
			"rect": text_rect,
			"handler": action
		}
	)

	screen.blit(button, text_rect)

	return button, text_rect

def changepage(page: str): locals.page = page

def refresh_page():
	while pygame.get_init():
		time.sleep(10)
		regis.refresh()
		moodle.refresh()

PromiseFuncWrap(refresh_page) # refresh every 10 secs

pygame.init()

info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h-100), pygame.RESIZABLE)
size = screen.get_size

# NOTE: FIGURE OUT HOW TO MOVE PYGAME WINDOW TO TOP

logo_box = pygame.transform.scale(
	pygame.image.load("assets/regis-logo-rectangle.png"),
	(280, 58)
)
logo_rect = logo_box.get_rect(topleft=(5, 5))

regis_icon = pygame.image.load("assets/regis-icon.png")
pygame.display.set_caption("Regis Intranet Desktop")
pygame.display.set_icon(regis_icon)

font = pygame.font.SysFont("Helvetica", 20, bold=True) # get actual font from site


# figure out how to make everything rounded

while 1:
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			for handler in BUTTON_HANDLERS:
				if handler["rect"].collidepoint(*pygame.mouse.get_pos()): handler["handler"]()
		if event.type == pygame.QUIT:
			pygame.quit()
			regis.quit()
			moodle.quit()
			exit(0)

	globals()[f"build_{locals.page}"]()

	pygame.display.update()