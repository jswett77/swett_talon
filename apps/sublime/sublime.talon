app: Sublime Text
--

reveal: key(ctrl-shift-alt-r)
pop: key(alt-[)
push: key(alt-])
enhance: key(ctrl-b)

find <user.sublime_find_type>: user.do_find(sublime_find_type)

# move lines up/down
^(pull|pole|poke)$: user.move_line(true)
^(bam)$: user.move_line(false)

backspace: key(backspace)

go|find named: key(cmd-p)
zoom in: key(cmd-shift-+)
zoom out: key(cmd-shift--)

tab close: key(cmd-w)
go tab next: key(ctrl-tab)
go tab previous: key(ctrl-shift-tab)
go tab <number>: user.tab_jump(number)

make it so: key(cmd-s)
down: key(down)
go up: key(up)

bet: key(cmd-d)
undo that: key(cmd-z)

nibble: key(alt-right)
peck: key(alt-left)

format looker query:
  key(esc)
  sleep(20ms)
  key(ctrl-a)
  sleep(75ms)
  key(shift-down)
  sleep(100ms)
  key(cmd-c)
  sleep(100ms)
  user.format_query(clip.text())