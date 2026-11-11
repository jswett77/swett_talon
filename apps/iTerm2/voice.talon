mode: all
app: iTerm2
-

^(wonder|wander)$:
  user.iterm_start_voice()

ten four | send it:
  user.iterm_finish_voice_and_scrub(0)

let it rip | let her rip | letter rip:
  user.iterm_finish_voice_and_scrub(1)

scrub tail | drop tail | chomp tail:
  user.iterm_scrub_trailing_keywords(0)

scrub send | chomp send:
  user.iterm_scrub_trailing_keywords(1)

^go tab <number_small>$:
  user.tab_jump(number_small)

stamp it | stampede:
  key(ctrl-k)
