# class Foo:
#     def __init__(self):
#         self.history = []

#     def reset(self):
#         self.history.clear()

#     def something(self): ...

# foo = Foo()

# @mod.action_class
# class Actions:
#     def some_action():
#         "does something"
#         foo.something()


# capture for sublime
# from typing import Dict
# from talon import Module, actions




# mod = Module()
# @mod.capture(rule="all | here")
# def sublime_find_type(m) -> str:
#     "Just map requested find"
#     if "all" in m:
#         return "all"
#     if "here" in m:
#         return "here"   


# @mod.action_class
# class FindActions:
#     def do_find(find_with: str):
#         """
#         Perform a search in sublimefff
#         """
#         print(find_with)
#         if find_with in "all":
#             actions.key("cmd-shift-f")
#             actions.key("del")
#         if find_with in "here":
#             actions.key("cmd-f")
#             actions.key("del")