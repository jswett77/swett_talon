mode: all
-
^focus chrome$: user.sleep_focus_app("chrome")
^focus chat$: user.sleep_focus_app("chat")
^focus (mail | gmail)$: user.sleep_focus_app("mail")
^focus (term | terminal | iterm)$: user.sleep_focus_app("term")
^focus remote$: user.sleep_focus_app("remote")
^focus (calendar | cal)$: user.sleep_focus_app("calendar")
