mode: all
app: iTerm2
-

^(wonder|wander)$:
  user.iterm_start_voice()

ten four | send it:
  user.iterm_finish_voice_and_scrub(0)

let it rip | let her rip | letter rip:
  user.iterm_finish_voice_and_scrub(1)

scrub tail | drop tail:
  user.iterm_scrub_trailing_keywords()

go tab <number>:
  user.tab_jump(number)

stamp it | stampede:
  key(ctrl-k)
