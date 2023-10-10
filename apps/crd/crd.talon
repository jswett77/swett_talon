app: Chrome Remote Desktop
language: en
-
# selection
chomp: key(alt-up)

# navigation

# goto def
enhance: key(ctrl-b) 

# go back 
pop: key(alt-[)

# return back
push: key(alt-])

find all: key(ctrl-shift-f)

find here: key(ctrl-f)

go named:
  key(shift)
  key(shift)

annotate:
  key(ctrl-alt-shift-s)

# cursor token right TODO digits
nibble: key(alt-right)

# cursor left TODO digits
peck: key(alt-left)

# center editor to cursor
center: key(alt-c)

go tab next: key(ctrl-t)
go tab previous: key(ctrl-shift-t)

go [to] stack: key(ctrl-shift-5)

tab close: key(ctrl-w)

goto line: key(ctrl-l)

swap tab: key(ctrl-shift-o)

replace all: key(ctrl-shift-w)

# show file in project viewer
reveal: key(ctrl-alt-shift-o)


# edit
undo that: key(ctrl-z)

# debugger
attach: key(alt-shift-f5)

# text size
zoom in: key(ctrl-shift-.)
zoom out: key(ctrl-shift-,)
zoom reset: key(ctrl-0)

# git related stuff

# for pasting git add
copy path: key(ctrl-alt-n)

 # revert current change to master
restore here: key(alt-shift-r)

# accept master during diff
accept here: key(ctrl-shift-r)

# open diffmouseufway not that impressive but let's say I sayl
git compare: key(ctrl-shift-d)

^run this test$:
  mouse_click(1)
  sleep(100ms)
  key(down:14)

^debug this test$:
  mouse_click(1)
  sleep(100ms)
  key(down:15)

sequel test:
  key(j)
  sleep(100ms)
  key(d)
  sleep(100ms)
  key(b)
  sleep(100ms)
  key(c)
  sleep(100ms)
  key(_)
  sleep(100ms)
  key(enter)

step over: key(f8)

step into: key(f7)

next stop: key(f9)

debug stop: key(alt-shift-2)

# toggles break point (remove or add)
break point: key(ctrl-alt-8)

# toggle enabled or not, leaves it there but "disables it" (or re-enables it)
disable break point: key(ctrl-alt-9)

# open settings
settings: key(alt-,)

# evaluate an expression
^(eval expression)$: key(ctrl-shift-8)

^evaluate$: key(ctrl-enter)

set pry:
  key(ctrl-a)
  sleep(50ms)
  key(enter)
  sleep(50ms)
  key(up)
  sleep(200ms)
  user.paste("Looker.pry(bindin9f9g)")
