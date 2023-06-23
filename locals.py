from contextlib import redirect_stdout
import datetime

with redirect_stdout(open("nul",'w')): import pygame

page = "homescreen"
cache: dict[str, str] = {}
cache_fails: dict[str, int] = {}

in_widget_add_menu = 0 # this is an int value used to set the height of the widget menu
SCHEDULE_COLOR_CYCLE = (
	(3, 252, 132),
	(219, 3, 252),
	(3, 123, 252),
	(204, 89, 51),
	(204, 51, 171),
	(196, 204, 51)
)
DEFAULT_TEXT_BACKGROUND_COLOR = (200, 50, 50)
DEFAULT_SCREEN_BACKGROUND_COLOR = (247, 244, 215)
DEFAULT_WIDGET_BACKGROUND_COLOR = (42, 219, 216)
DEFAULT_WIDGET_MENU_BACKGROUND_COLOR = (149, 255, 125)
HEIGHT_PX_15_MIN = 90
BUTTON_HOVER_COLOR = (166, 5, 5)
NOTICE_COLOR = (50, 168, 168)
BEFORE_NORMAL_TIME = datetime.time(8, 15)
BEFORE_LATE_TIME = datetime.time(9)
LAST_MOD_END = datetime.time(15, 15)
SCROLL_OFFSET = 0
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
ALLOWED_WIDGETS = {
	"currentClass": "Current & Next Class",
	"communityTime": "Community Time Events"
}
WIDGET_SURFS: dict[str, dict[str, pygame.Surface, pygame.Rect]] = {
    # name: {
	#   "surf": pygame.Surface,
	#	"rect": pygame.Rect
	# }
}