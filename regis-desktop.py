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

def get_current_class_widget(largefont: pygame.font.Font, document: Document):
	surf = pygame.Surface((500, 230))

	surf.fill(DEFAULT_SCREEN_BACKGROUND_COLOR)

	pygame.draw.rect(surf, DEFAULT_WIDGET_BACKGROUND_COLOR, (0, 0, *surf.get_size()), border_radius=7)

	letter_day = get_letter_day(document.querySelector("#myprimarykey_43 > div > div > div:nth-child(4)"))

	letter_day = 'A'

	if letter_day == "not a school/letter":
		surf.blit(
			largefont.render("Today isn't a school/letter day!", True, "black"),
			(10, 10)
		)
		
		return surf

	normal_classes, late_classes = utils.get_current_and_next_class(
		document.querySelector("#myprimarykey_43 > div > div > div:nth-child(6)").children[string.ascii_uppercase.index(letter_day)+1]
	)

	surf.blit(
		largefont.render("Normal Timing", True, "black"),
		(10, 10)
	)

	surf.blit(
		largefont.render("Late Start Timing", True, "black"),
		(10, 130)
	)

	surf.blit(
		get_default_text(f"Current Mod: {normal_classes[0]}", "black"),
		(10, 50)
	)

	surf.blit(
		get_default_text(f"Next Mod: {normal_classes[1]}", "black"),
		(10, 80)
	)

	surf.blit(
		get_default_text(f"Current Mod: {late_classes[0]}", "black"),
		(10, 170)
	)

	surf.blit(
		get_default_text(f"Next Mod: {late_classes[1]}", "black"),
		(10, 200)
	)

	surf_rect = surf.get_rect(topleft=(10, 130+locals.SCROLL_OFFSET))

	def update(values: dict[str]):
		if "parent_rect" in values: return

		values["parent_rect"] = surf_rect

	make_button_using_surf(
		"Delete Widget",
		del_widget_icon,
		lambda: CONFIG["userWidgets"].remove("currentClass"),
		(surf.get_width()-del_widget_icon.get_width(), 0),
		"delete-current-class-widget",
		update=update,
		blit_to=surf
	)

	return surf, surf_rect

def get_community_time_widget(document: Document):
	maxwidth = int(size()[0]*(3/4)-50)

	try: surf = pygame.Surface((maxwidth-(size()[0]*(1/3)), 400))
	except pygame.error: # invalid surf res, this means the screen is too small to view this widget anyway
		surf = pygame.Surface((1, 1)) # allocate a tiny surf to return
		return surf, surf.get_rect(topleft=(700, 75))

	surf.fill(DEFAULT_SCREEN_BACKGROUND_COLOR)

	pygame.draw.rect(surf, DEFAULT_WIDGET_BACKGROUND_COLOR, (0, 0, *surf.get_size()), border_radius=7)

	events_parent = document.querySelector("#myprimarykey_44 > div > div > div.row > div > div > div.panel-body > table > tbody")
	if events_parent: events_list = [
		f"{child.firstElementChild.firstElementChild.textContent.strip()} ({child.lastElementChild.textContent.strip()})"
		for child in events_parent.children
	]
	else: events_list = ["No Community Events Today :("]

	build_list_box_on_surf(
		surf,
		events_list,
		"Today's Events",
		(5, 5),
		maxwidth,
		title_color="black",
		title_bg=DEFAULT_WIDGET_BACKGROUND_COLOR
	)

	surf_rect = surf.get_rect(topleft=(700, 75+locals.SCROLL_OFFSET))

	def update(values: dict[str]):
		if "parent_rect" in values: return

		values["parent_rect"] = surf_rect

	make_button_using_surf(
		"Delete Widget",
		del_widget_icon,
		lambda: CONFIG["userWidgets"].remove("communityTime"),
		(surf.get_width()-del_widget_icon.get_width(), 0),
		"delete-community-time-widget",
		update=update,
		blit_to=surf,
	)

	return surf, surf_rect

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

	make_button("Assignments :)", lambda: changepage("assignments"), (5, 400), "see-assns")
	make_button("Schedule :)", lambda: changepage("schedule"), (5, 430), "see-schedule")

	width, height = size()

	make_button_using_surf(
		"Add Widget",
		add_widget_icon,
		widget_button_onclick,
		(width-50, height-50),
		"add-widget-btn",
		widget_button_rotate,
		widget_button_update
	)

	if "currentClass" in CONFIG["userWidgets"]:
		widget, rect = get_current_class_widget(largefont, document)
		
		screen.blit(
			widget,
			rect,
		)

		locals.WIDGET_SURFS["currentClass"] = {
			"surf": widget,
			"rect": rect
		}
	if "communityTime" in CONFIG["userWidgets"]:
		widget, rect = get_community_time_widget(document)
		
		screen.blit(
			widget,
			rect,
		)

		locals.WIDGET_SURFS["currentClass"] = {
			"surf": widget,
			"rect": rect
		}

	# TODO: add events next to the current/next mod section

def build_list_box_on_surf(surf: pygame.Surface, _list: list, title: str, pos: tuple[int, int], maxwidth: int, color_cycle: tuple[pygame.Color]=("black",), background_color_cycle: tuple[pygame.Color]=(None,), title_color: pygame.Color="white", title_bg: pygame.Color=DEFAULT_TEXT_BACKGROUND_COLOR, buttonize: dict={}):
	lines, line_parent_map = utils.wrap_text(_list, int(maxwidth/font.size('m')[0]))

	surf.blit(
		get_default_text(title, title_color, title_bg),
		pos
	)

	for i, line in enumerate(lines):
		parent_lineno = line_parent_map[i]

		if parent_lineno in buttonize.keys():
			make_button(
				line, buttonize[parent_lineno],
				(pos[0], ((i*30)+50+pos[1])-locals.SCROLL_OFFSET), # subtract scroll offset to negate make_button's effects
				f"buttonized-{secrets.token_urlsafe(5)}",
				color=color_cycle[parent_lineno%len(color_cycle)],
				background_color=background_color_cycle[parent_lineno%len(background_color_cycle)],
				surf=surf
			)

			continue

		surf.blit(
			get_default_text(line, color=color_cycle[parent_lineno%len(color_cycle)], background=background_color_cycle[parent_lineno%len(background_color_cycle)]),
			(pos[0], (i*30)+50+pos[1])
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

def widget_button_onclick():
	locals.in_widget_add_menu = int(info.current_h*(2/3)) # set the widget menu height cap to the maximum for the menu

def widget_button_rotate(values: dict[str, int | pygame.Surface | pygame.Rect]):
	surf_center = values["rect"].center

	if values.get("rotated"):
		if values["rotated"] == 90:
			values["surf"] = pygame.transform.rotate(add_widget_icon, -(values["rotated"]+5))
			values["rect"] = values["surf"].get_rect(center=surf_center)
			return
		
		values["rotated"]+=10
	else: values["rotated"] = 10

	values["surf"] = pygame.transform.rotate(add_widget_icon, -values["rotated"])
	values["rect"] = values["surf"].get_rect(center=surf_center)

def widget_button_update(values: dict[str, int | pygame.Surface | pygame.Rect]):
	if not values.get("rotated"): return

	surf_center = values["rect"].center

	values["rotated"]-=5

	values["surf"] = pygame.transform.rotate(add_widget_icon, -values["rotated"])
	values["rect"] = values["surf"].get_rect(center=surf_center)	

def default_button_hover(values: dict[str]):
	values["background_color"] = BUTTON_HOVER_COLOR

def default_button_update(values: dict[str]):
	try: values.pop("background_color") # let the next call decide the color
	except KeyError: pass

def make_button_using_surf(text: str, surf: pygame.Surface, action: Callable[[], None], pos: tuple[int, int], _id: str, hover: Callable[[dict[str]], None]=default_button_hover, update: Callable[[dict[str]], None]=default_button_update, blit_to: pygame.Surface=None, force_update: bool=False):
	blit_to = blit_to if blit_to else screen
	
	id_exists = BUTTON_HANDLERS.get(_id) and (not force_update)
	if id_exists:
		values = BUTTON_HANDLERS[_id]["values"]

		surf = values.get("surf", surf)

		action = BUTTON_HANDLERS[_id]["handler"]
		hover = BUTTON_HANDLERS[_id]["hover"]
		update = BUTTON_HANDLERS[_id]["update"]

		values["surf"] = surf
	else: values = {}

	rect = values.get("rect", surf.get_rect(topleft=(pos[0], pos[1]+locals.SCROLL_OFFSET)))

	if not id_exists:
		BUTTON_HANDLERS[_id] = {
			"rect": rect,
			"handler": action,
			"hover": hover,
			"update": update,
			"values": {
				"text": text,
				"rect": rect,
				"surf": surf,
				"color": None,
				"background_color": None
			}
		}

	blit_to.blit(surf, rect)

	return surf, rect

def make_button(text: str, action: Callable[[], None], pos: tuple[int, int], _id: str, hover: Callable[[dict[str]], None]=default_button_hover, update: Callable[[dict[str]], None]=default_button_update, color: pygame.Color="white", background_color: pygame.Color="red", surf: pygame.Surface=None):
	surf = surf if surf else screen
	
	id_exists = BUTTON_HANDLERS.get(_id)
	if id_exists:
		values = BUTTON_HANDLERS[_id]["values"]

		text, color, background_color = values.get("text", text), values.get("color", color), values.get("background_color", background_color)
		action = BUTTON_HANDLERS[_id]["handler"]
		hover = BUTTON_HANDLERS[_id]["hover"]
		update = BUTTON_HANDLERS[_id]["update"]	
	else: values = {}
	
	text_surf = get_default_text(text, color)
	size = text_surf.get_size()
	
	button = pygame.Surface((size[0]+10, size[1]+5))
	button.fill(DEFAULT_SCREEN_BACKGROUND_COLOR)

	# rounded background
	pygame.draw.rect(button, background_color, (0, 0, *button.get_size()), border_radius=7)

	button.blit(text_surf, (5, 0))

	text_rect = button.get_rect(topleft=(pos[0], pos[1]+locals.SCROLL_OFFSET))
	
	BUTTON_HANDLERS[_id] = {
		"handler": action,
		"hover": hover,
		"update": update,
		"values": {
			"text": text,
			"rect": text_rect,
			"color": color,
			"background_color": background_color
		}
	}

	surf.blit(button, text_rect)

	return button, text_rect

def build_widget_menu(maxheight: int):
	display: list[tuple[str, pygame.Surface]] = []

	for widget in (widget for widget in locals.ALLOWED_WIDGETS if widget not in CONFIG["userWidgets"]):
		text = locals.ALLOWED_WIDGETS[widget]

		text_surf = get_default_text(text, background=DEFAULT_WIDGET_BACKGROUND_COLOR)
		text_size = text_surf.get_size()

		surf = pygame.Surface((text_size[0]+10, text_size[1]+6))
		surf.fill(DEFAULT_WIDGET_MENU_BACKGROUND_COLOR)

		pygame.draw.rect(surf, DEFAULT_WIDGET_BACKGROUND_COLOR, (0, 0, *surf.get_size()), border_radius=7)
		surf.blit(text_surf, (5, 3))

		display.append((widget, surf))

	if not display:
		display.append(
			("nullWidget", get_default_text("Nothing to see here...", background=DEFAULT_WIDGET_MENU_BACKGROUND_COLOR))
		)

	# the +10 on each widget is for padding
	total_height = min(
		sum(surf.get_height()+10 for (_id, surf) in display)+50, # +50 for bottom padding
		maxheight
	)
	
	max_width = max(display, key=lambda tup: tup[1].get_width())[1].get_width()
	
	menu_width = max_width+20 # padding

	menu = pygame.Surface((menu_width, total_height))
	menu.fill(DEFAULT_SCREEN_BACKGROUND_COLOR)

	pygame.draw.rect(
		menu,
		DEFAULT_WIDGET_MENU_BACKGROUND_COLOR,
		(0, 0, *menu.get_size()),
		border_top_left_radius=7,
		border_bottom_left_radius=7
	)

	# have the menu just above the button
	x, y = size()
	rect = menu.get_rect(bottomright=(x, y-BUTTON_HANDLERS["add-widget-btn"]["values"]["surf"].get_height()))

	curr_y = 10

	def update(vals: dict[str]):
		if "parent_rect" in vals: return

		vals["parent_rect"] = rect

	for (_id, widget_surf) in display:
		make_button_using_surf(
			"Add Widget",
			widget_surf,
			lambda: CONFIG["userWidgets"].append(_id),
			(10, curr_y),
			f"add-widget [{_id}]",
			update=update,
			blit_to=menu,
			force_update=True
		)

		curr_y+=10+widget_surf.get_height()

	return menu, rect

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

add_widget_icon = pygame.transform.scale(
	pygame.image.load("assets/plus-icon.png"),
	(50, 50)
)

del_widget_icon = pygame.transform.scale(
	pygame.image.load("assets/del-icon.png"),
	(20, 20)
)

widget_menu, widget_menu_rect = (None, None)

while 1:
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			if logo_rect().collidepoint(*pygame.mouse.get_pos()): changepage("homescreen")
			# click button
			try:
				mouse_pos = pygame.mouse.get_pos()
				for handler in BUTTON_HANDLERS.values():
					if "parent_rect" in handler["values"]:
						parent_rect: pygame.Rect = handler["values"]["parent_rect"]

						mouse_pos: tuple[int, int] = (mouse_pos[0]-parent_rect.topleft[0], mouse_pos[1]-parent_rect.topleft[1])

					if handler["values"]["rect"].collidepoint(mouse_pos): handler["handler"]()
			except RuntimeError as e:
				if str(e) == "dictionary changed size during iteration": continue # this means the page changed and BUTTON_HANDLERS was cleared
				raise
		if event.type == pygame.MOUSEWHEEL:
			locals.SCROLL_OFFSET = min(max(locals.SCROLL_OFFSET+event.y*10, -800), 0)
		if event.type == pygame.QUIT:
			pygame.quit()
			utils.write_config(CONFIG)
			utils.write_nonvolatile_cache()
			regis.quit()
			regisauxpage.quit()
			moodle.quit()
			exit(0)

	mouse_pos = pygame.mouse.get_pos()

	# hover effect for buttons
	for handler in BUTTON_HANDLERS.values():
		if handler["values"]["rect"].collidepoint(*mouse_pos): handler["hover"](handler["values"])
		
	globals()[f"build_{locals.page}"]()

	if locals.in_widget_add_menu:
		widget_menu, widget_menu_rect = build_widget_menu(locals.in_widget_add_menu)
		screen.blit(widget_menu, widget_menu_rect)

		if widget_menu_rect.collidepoint(*mouse_pos) or (BUTTON_HANDLERS["add-widget-btn"]["values"]["rect"].collidepoint(*mouse_pos)):
			# if the mouse is hovering over the widget OR the button, then bring the menu up more
			locals.in_widget_add_menu = min(
				locals.in_widget_add_menu+10,
				int(info.current_h*2/3)
			)
		else:
			# otherwise, shrink the menu down
			locals.in_widget_add_menu = max(
				min(locals.in_widget_add_menu-10, widget_menu.get_height()),
				0
			)

	if (
		(locals.page == "homescreen") and BUTTON_HANDLERS["add-widget-btn"]["values"]["rect"].collidepoint(*mouse_pos)
	):
		locals.in_widget_add_menu = min(
			locals.in_widget_add_menu+10,
			int(info.current_h*2/3)
		)


	# button update func
	for handler in BUTTON_HANDLERS.values(): handler["update"](handler["values"])

	pygame.display.update()