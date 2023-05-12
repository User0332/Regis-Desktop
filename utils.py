from domapi import Element
from contextlib import redirect_stdout
from locals import *
import datetime
import textwrap
import tinycss

with redirect_stdout(open("nul",'w')): import pygame

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

def parse_schedule(schedule_div: Element) -> list[str]:
	classes = []

	for child in schedule_div.children:
		if child.textContent.strip() == "":
			classes.append("Free") # free mod color
			continue
		
		classes.append(
			child.textContent.strip()
			.replace("\n\n", ' ')
			.replace('\n', ' ')
			.replace(" | Zoom", '')
		)

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

				classes.extend([child.textContent.strip().replace('\n', ' ')]*num_blocks)
				break

		while "" in classes: classes[classes.index("")] = "Free"

	return (
		{ TIMES[i]: _class for i, _class in enumerate(classes) },
		{ LATE_TIMES[i]: _class for i, _class in enumerate([x for x in classes if x != "Community Time"]) }
	)