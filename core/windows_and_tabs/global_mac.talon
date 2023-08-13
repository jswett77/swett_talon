os: mac
-
# Mission control
show apps: key(ctrl-up)

# All windows for app
fomo: key(ctrl-down)

# escape
meh: key(esc)

# logout
logout: key(cmd-ctrl-q)

# toggle between recent apps
^(what what)+$: key(cmd-tab)


# finder
^(launch finder)$:
	key("cmd-space")
	sleep(10ms)
	insert("Finder")
	sleep(100ms)
	key("enter")
	