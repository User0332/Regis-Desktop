from domapi import Element, make_document_from_str
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By as ElementFindMethod
from contextlib import redirect_stdout
from dataclasses import dataclass
from typing import TypedDict
from locals import *
import datetime
import textwrap
import tinycss
import perfcount
import locals
import json
import os

with redirect_stdout(open(NULL_DEV,'w')): import pygame

class GradeTrackerAssignmentEntry(TypedDict):
	name: str
	grade: float
	category: str

class GradeTrackerClass(TypedDict):
	weights: dict[str, float]
	entries: list[GradeTrackerAssignmentEntry]

GradeTrackerConfig = dict[str, GradeTrackerClass]

class Assignment(TypedDict):
	date: str
	description: str

@dataclass
class Planner:
	name: str
	assignments: list[Assignment]
	notes: list[str]

def wrap_text(lines: list[str], width: int):
	total_lines: int = 0
	parent_map: dict[int, int] = {}

	for i, line in enumerate(lines):
		lines[i] = textwrap.wrap(line, width-2)

		for j, subline in enumerate(lines[i]):
			parent_map[total_lines] = i
			
			total_lines+=1

			if j == 0: continue
			lines[i][j] = f"    {subline}"

	return [line for wrapped in lines for line in wrapped], parent_map

def strip_class(_class: str) ->  str:
	return (
		_class.strip()
		.replace("\n\n", ' ')
		.replace('\n', ' ')
		.replace(" | Zoom", '')
	)

def parse_schedule(schedule_div: Element) -> list[str]:
	classes = []

	for child in schedule_div.children:
		if child.textContent.strip() == "":
			classes.append("Free") # free mod color
			continue
		
		classes.append(strip_class(child.textContent))

	free_mins = 0

	for i, item in enumerate(classes): #concat frees
		if item == "Free":
			free_mins+=15

		if ((item != "Free") or (i == len(classes)-1)) and (i > 0) and (classes[i-1] == "Free"):
			classes.insert(i, f"{free_mins}min Free")
			free_mins = 0

	while "Free" in classes: classes.remove("Free")

	return classes
	
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

				classes.extend([strip_class(child.textContent)]*num_blocks)
				break

		while "" in classes: classes[classes.index("")] = "Free"

	late_classes = classes[:8]+classes[11:] # remove 10:30 - 11:15

	if "Assembly" in late_classes: late_classes[late_classes.index("Assembly")] = "Assembly (Probably Free)"


	return (
		{ TIMES[i]: _class for i, _class in enumerate(classes) },
		{ LATE_TIMES[i]: _class for i, _class in enumerate(late_classes) }
	)

def cache_get_src(browser: Chrome, url_accessing: str="https://intranet.regis.org/", milliseconds: int=30):
	res = perfcount.timeout(milliseconds=milliseconds)(lambda: browser.page_source)()

	cache_res = locals.cache.get(url_accessing)

	if res is None:
		# print(f"info: {url_accessing} took too long, trying cache") # removed print statement because it slows down the application
		if (cache_res is None) or (locals.cache_fails.get(url_accessing) == 1000): # we must wait for the page and update the cache in this case, it has failed too many times OR there is no cache data available to send
			locals.cache_fails[url_accessing] = 0
			src = locals.cache[url_accessing] = browser.page_source
			return src
		else:
			locals.cache_fails[url_accessing]+=1
			return cache_res

	locals.cache[url_accessing] = res
	locals.cache_fails[url_accessing] = 0

	return res

def get_today_and_tmrw_letter_day(timehighlight: Element, regisaux: Chrome) -> tuple[str, str, bool, bool]:
	# return fmt
	# return day1, day2, latestart1, latestart2

	parent = Element(timehighlight._root.getparent())

	try: letter_day = parent.getElementsByTagName("letterday")[0].textContent.strip()
	except IndexError: letter_day = "not a school/letter"

	late_start = bool(parent.getElementsByTagName("timeorder"))

	sib = parent._root.getnext()

	if sib is None:
		weeksib = parent._root.getparent().getnext()

		if weeksib is None: # next month
			regisaux.find_element(ElementFindMethod.CSS_SELECTOR, "body > div > div > div > div:nth-child(2) > div.col-md-6 > div:nth-child(4) > a").click()

			nextmonthdoc = make_document_from_str(
				cache_get_src(
					regisaux,
					"https://intranet.regis.org/calendar?nextmonth"
				)
			)
			
			next_day_parent = nextmonthdoc.querySelector("body > div > div > div > div.calendar > div:nth-child(2) > div:not(.nonMonthDay)")

			try: next_letter_day = next_day_parent.getElementsByTagName("letterday")[0].textContent.strip()
			except IndexError: next_letter_day = "not a school/letter"

			next_late_start = bool(next_day_parent.getElementsByTagName("timeorder"))


			return letter_day, next_letter_day, late_start, next_late_start # TODO: find out next month day

		sib = weeksib.getchildren()[0]

	next_day_parent = Element(sib)

	try: next_letter_day = next_day_parent.getElementsByTagName("letterday")[0].textContent.strip()
	except IndexError: next_letter_day = "not a school/letter"

	next_late_start = bool(next_day_parent.getElementsByTagName("timeorder"))

	return letter_day, next_letter_day, late_start, next_late_start

def get_current_and_next_class(schedule_div: Element) -> str:
	normal_schedule, late_schedule = schedule_convert_15min(schedule_div)

	curr_time = datetime.datetime.now().time()

	normal_classes = ["No class!", "No class!"]
	late_classes = ["No class!", "No class!"]

	for i, classtime in enumerate(normal_schedule.keys()):
		if (i == 0) and (curr_time < classtime) and (curr_time > BEFORE_NORMAL_TIME):
			normal_classes[1] = normal_schedule[classtime]
			break

		if (curr_time < classtime) and (curr_time > tuple(normal_schedule.keys())[i-1]):
			normal_classes = [tuple(normal_schedule.values())[i-1], normal_schedule[classtime]]
			break

	for i, classtime in enumerate(late_schedule.keys()):
		if (i == 0) and (curr_time < classtime) and (curr_time > BEFORE_LATE_TIME):
			late_classes[1] = late_schedule[classtime]
			break
		
		if (curr_time < classtime) and (curr_time > tuple(late_schedule.keys())[i-1]):
			late_classes = [tuple(late_schedule.values())[i-1], late_schedule[classtime]]
			break
	
	if (curr_time < LAST_MOD_END) and (curr_time > TIMES[-1]):
		normal_classes[0] = tuple(normal_schedule.values())[-1]
		late_classes[0] = tuple(normal_schedule.values())[-1]

	return normal_classes, late_classes

def was_created_today(file: str) -> bool:
	today = datetime.datetime.now().date()
	return datetime.datetime.fromtimestamp(os.stat(file).st_mtime).date() == today

def write_nonvolatile_cache():
	for i, (site, data) in enumerate(locals.cache.items()):
		with open(f"cache/{i}", 'w', encoding="utf-8") as f:
			f.write(f"{site}\n{data}")

def load_nonvolatile_cache():
	for file in os.listdir("cache"):
		if not was_created_today(f"cache/{file}"):
			os.remove(f"cache/{file}")
			continue # old file, remove
		
		with open(f"cache/{file}", 'r', encoding="utf-8") as f:
			split = f.read().splitlines()
			locals.cache[split[0]] = '\n'.join(split[1:])
			locals.cache_fails[split[0]] = 0

def load_planners() -> list[Planner]:
	planners = []

	for plannerfile in os.listdir("installation/planners"):
		data = json.load(open(f"installation/planners/{plannerfile}", 'r'))

		planners.append(
			Planner(data["name"], data["assignments"], data["notes"])
		)

	return planners

def load_config() -> dict[str, str | list[str]]:
	conf: dict[str, str | list[str]] = json.load(open("installation/config.json"))

	# if not conf.get("profilePath"):
	# 	# make this a gui message
	# 	print("Fatal Error: Chrome profile path not specified in config! Run the Regis Desktop Installer to configure (unable to autofix)")
	# 	exit(1)

	widgets: list[str] = conf.get("userWidgets")

	if widgets is None:
		print("Error: User widgets not specified -- autofixing")
		conf["userWidgets"] = []

	for widget in widgets:
		if widget not in ALLOWED_WIDGETS:
			print(f"Error: The widget {widget!r} from the config is not a valid widget! -- autofixing")
			conf["userWidgets"].remove(widget)

		if widgets.count(widget) > 1:
			print(f"Error: The widget {widget!r} from the config is specified more than once! -- autofixing")		
			while widgets.count(widgets) != 1: widgets.remove(widget)

	return conf

def write_config(conf: dict[str, str | list[str]]):
	json.dump(conf, open("installation/config.json", 'w'), indent='\t')

def load_grade_tracker() -> GradeTrackerConfig:
	conf: GradeTrackerConfig = json.load(open("installation/grades.json", 'r'))

	# TODO: validate config

	return conf

def write_grade_tracker(conf: GradeTrackerConfig):
	json.dump(conf, open("installation/grades.json", 'w'))

def calc_grades_percentage(weights: list[float], entries: list[GradeTrackerAssignmentEntry]) -> tuple[dict[str, tuple[float, float]], float]: # (percent_contribution_for_each_category, final_grade)
	category_contrib: dict[str, float] = {
		category: 0 for category in weights
	}

	category_num_assns: dict[str, int] = {
		category: 0 for category in weights
	}

	categories_with_contrib: dict[str, bool] = {
		category: False for category in weights
	}

	for entry in entries:
		if categories_with_contrib[entry["category"]] is False:
			categories_with_contrib[entry["category"]] = True

		category_contrib[entry["category"]]+=entry["grade"]
		category_num_assns[entry["category"]]+=1

	for category in (key for key in categories_with_contrib if not categories_with_contrib[key]):
		category_contrib[category] = 1
		category_num_assns[category] = 1

	new_category_contrib: dict[str, tuple[float, float]] = {
		category: ((val/category_num_assns[category])*weights[category]*100, ((val/category_num_assns[category])*100)) for category, val in category_contrib.items()
	}

	return new_category_contrib, sum(item[0] for item in new_category_contrib.values())