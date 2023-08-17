app: chrome
and os: mac
-
search: key(cmd-l)
moma:
	key(cmd-l)
	key(m)
	key(tab)
helltool | (goto) hell:
	key(cmd-l)
	key(h)
	key(t)
	key(tab)

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
