# capture for sublime
from typing import Dict
from talon import Context, Module, actions, app

mod = Module()
@mod.capture(rule="all | here")
def sublime_find_type(m) -> str:
	"Just map requested find"
	if "all" in m:
		return "all"
	if "here" in m:
		return "here"	


ctx = Context()


@mod.action_class
class FindActions:
	def do_find(find_with: str):
		"""
		Perform a search in sublimefff
		"""
		print(f"do_find called with: {find_with}")
		if find_with in "all":
			actions.key("cmd-shift-f")
			actions.key("del")
		if find_with in "here":
			actions.key("cmd-f")
			actions.key("del")


@mod.action_class
class MovementActions:
	def move_line(up: bool):
		"""
		Sublime move line up/down
		"""
		direction = "up" if up else "down"
		# actions.key(f"cmd-ctrl-{direction}")

@mod.action_class
class tab_actions:
    def tab_jump(number: int):
    	"""Jump to a tab"""
    	if number < 9:
        	actions.key(f"cmd-{number}")

    def tab_final():
        """Jumps to the final tab"""

    def tab_close_wrapper():
        """Closes the current tab.
        Exists so that apps can implement their own delay before running tab_close() to handle repetitions better.
        """
        actions.app.tab_close()

    def tab_duplicate():
        """Duplicates the current tab."""