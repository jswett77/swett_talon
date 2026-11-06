mode: all
-
[window] (window next | next window | cycle window):
    user.sleep_window_next()

[window] (window (last | previous) | (last | previous) window):
    user.sleep_window_previous()

^snap <user.window_snap_position>$:
    user.snap_window(window_snap_position)

^snap next [screen]$:
    user.move_window_next_screen()

^snap last [screen]$:
    user.move_window_previous_screen()

^snap screen <number>$:
    user.move_window_to_screen(number)

^snap <user.running_applications> <user.window_snap_position>$:
    user.snap_app(running_applications, window_snap_position)

^snap <user.running_applications> [screen] <number>$:
    user.move_app_to_screen(running_applications, number)
