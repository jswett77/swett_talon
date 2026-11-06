mode: all
-
^drowse [<phrase>]$:
    speech.disable()

^(no cap|raptors)+$:
    speech.enable()
    user.mouse_wake()

^(talon wake)+$:
    speech.enable()
    user.mouse_wake()
