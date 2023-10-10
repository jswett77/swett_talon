# defines the default edit actions for linux
from talon import Module, Context, actions, clip

# ctx = Context()
# ctx.matches = r"""
# os: mac
# and app: chrome
# """
# @ctx.action_class("user")

mod = Module()
@mod.action_class
class seach_actions:
    def find_here(search: str):
        """Invoke chrome find, optionally with a search string"""
        actions.key("esc")
        actions.key("cmd-f")
        paste_clipboard = search in "clipboard" or search in "clip board"
        if paste_clipboard:
            #clipboard_val = actions.edit.paste() # use this if you want to invoke "cmd-v"
            clipboard_val = actions.clip.text()
            print(f"clip val = {clipboard_val}")
            actions.insert(clipboard_val)
            actions.key("enter")
        if search not in "nope" and not paste_clipboard:
            actions.key("cmd-f")
            actions.insert(search)
            actions.key("enter")