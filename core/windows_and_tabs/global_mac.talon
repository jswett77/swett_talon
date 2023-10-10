os: mac
-
# Mission control
show apps: key(ctrl-up)

# All windows for app
^(fomo|show all|birds eye)$: key(ctrl-down)

# escape
meh: key(esc)

# logout
logout: key(cmd-ctrl-q)

# toggle between recent apps
^(what what)+$: key(cmd-tab)

# finder, other apps
^(launch|open) <user.text>:
	key("cmd-space")
	sleep(10ms)
    
	insert(text)
	sleep(100ms)
	key("enter")
	
^(close this)$:
    key(cmd-w)

# move to other dispaly
# ^(punt this)$:
#	key(cmd-ctrl-alt-right)
# Use "snap next" instead111

grab screen shot:
    key(cmd-ctrl-shift-4)

new isntance:
    key(cmd-n)


# Rectangle Window Management
window zoom out:
	key(cmd-ctrl-alt--)
	key(cmd-ctrl-alt--)
	key(cmd-ctrl-alt--)

window zoom in:
	key(cmd-ctrl-alt-=)	
	key(cmd-ctrl-alt-=)	
	key(cmd-ctrl-alt-=)	
	