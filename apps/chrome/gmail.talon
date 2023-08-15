app: gmail
-
#   Jumping
# g then i :  Go to Inbox
inbox:
  key(esc)
  sleep(100ms)
  key(g)
  key(i)

# g then s :  Go to Starred conversations

# g then b :  Go to Snoozed conversations
# g then t :  Go to Sent messages
sent:
  key(esc)
  sleep(100ms)
  key(g)
  key(t)

# g then d :  Go to Drafts
go drafts:
  key(esc)
  key(g)
  key(d)



# g then a :  Go to All mail
# g then c :  Go to Contacts
# g then l :  Go to Label
# g then k :  Go to Tasks
# ⌘ + ⌥ + 1 : Open Mail
# ⌘ + ⌥ + 2 : Open Chat
# ⌘ + ⌥ + 3 : Open Spaces
# ⌘ + ⌥ + 4 : Open Meet
# g then f :  Go to search filters
# Threadlist selection
# * then a :  Select all conversations
# * then n :  Deselect all conversations
# * then r :  Select read conversations
# * then u :  Select unread conversations
# * then s :  Select starred conversations
# * then t :  Select unstarred conversations
# Navigation
# u : Back to threadlist
# k / j : Newer/older conversation
# o or Enter :  Open conversation; collapse/expand conversation
# p / n : Read previous/next message
# g then n :  Go to next page
# g then p :  Go to previous page
# ` : Go to next inbox section
# ~ : Go to previous inbox section
# ⌘ + ⌥ + v : Reset sidebar sections to default height
# Application
# / : Search mail
find [all]:
  key(esc)
  key(/)
# ? : Open keyboard shortcut help
# q : Search chat contacts

# c : Compose
compose mail:
  key(c)

# d : Compose in a tab
# . : Open "more actions" menu
# v : Open "move to" menu
# l : Open "label as" menu
# Actions
# , : Move focus to toolbar

# x : Select conversation
select this:
  key(x)

# s : Toggle star/Rotate among superstars
# y : Remove label
# e : Archive

# m : Mute conversation
mute this:
  key(m)

# ! : Report as spam
# # : Delete
delete this:
  key(#)

# r : Reply
reply:
  key(r)

# Shift + r : Reply in a new window
# a : Reply all
# Shift + a : Reply all in a new window
# f : Forward
# Shift + f : Forward in a new window
# Shift + n : Update conversation
# ] / [ : Remove conversation from current view and go newer/# older
# } / { : Archive conversation and go newer/older
# z : Undo last action
# Shift + i : Mark as read
# Shift + u : Mark as unread
# _ : Mark unread from the selected message
# + or = :  Mark as important
# - : Mark as not important

# ; : Expand entire conversation
go expand:
  key(;)

# : : Collapse entire conversation
go compact:
  key(:)
# b : Snooze
# Shift + t : Add conversation to Tasks
# Google Chat
# h then c :  Focus on the conversation list
# h then r :  Focus on the spaces list10b