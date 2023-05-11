import textwrap
import functools

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

def parse_schedule(content: str) -> list[str]:
	unfiltered = [
		(
		item.replace("  ", '')
			.replace("   ", '')
			.replace("    ", '')
			.replace("     ", '')
			.replace('\n', ' ')
			.replace("       ", '') # final whitespace cleanup
			.strip()
			if not item.replace(' ', '').replace('\n', '') == ''  
			else "Free"
		) for item in
		content.replace(" | Zoom", '')
			.split("\n     \n     \n")[1:-1]
		if item not in ("     ")
	]

	free = 0

	for i, item in enumerate(unfiltered): #concat frees
		if item == "Free":
			free+=15

		if ((item != "Free") or (i == len(unfiltered)-1)) and (i > 0) and (unfiltered[i-1] == "Free"):
			unfiltered.insert(i, f"{free}min Free")

	while "Free" in unfiltered: unfiltered.remove("Free")

	return unfiltered
	
