# capture for sublime
from typing import Dict
from talon import Context, actions, app

ctx = Context()
ctx.matches = r"""
os: mac
and app: iTerm2
and title: /hell\d*|brap|tmux/
"""


@ctx.action_class("user")
class tab_actions:
    def tab_jump(number: int):
        """Jump to a tab"""
        if number <= 9:
            actions.key("ctrl-b")
            actions.sleep("30ms")
            actions.key(f"{number}")