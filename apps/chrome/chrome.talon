app: chrome
and os: mac
-
search: key(cmd-l)

# consistency with 
pop: key(cmd-[)
push: key(cmd-])

mute me:
	key(cmd-d)

find here [<user.text>]: 
	user.find_here(text or "nope")

next:
	key(enter)


profile switch: user.chrome_mod("shift-m")

tab search: user.chrome_mod("shift-a")

tab search <user.text>$:
    user.chrome_mod("shift-a")
    sleep(200ms)
    insert("{text}")
    key(down)

# emulate opening in new tab
detach tab:
	key(cmd-l)
	sleep(100ms)
	key(cmd-c)
	sleep(100ms)
	key(cmd-w)
	sleep(100ms)
	key(cmd-n)
	key(cmd-l)
	key(cmd-v)
	key(enter)
