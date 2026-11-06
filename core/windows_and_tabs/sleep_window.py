from talon import Module, actions, app, ui

mod = Module()


def _get_app_windows(active_app: ui.App) -> list[ui.Window]:
    """Returns focusable, non-hidden windows for the application."""
    try:
        windows = [
            w
            for w in active_app.windows()
            if not w.hidden and not w.minimized and (w.title or len(active_app.windows()) == 1)
        ]
        return windows
    except Exception as e:
        print(f"[sleep_window] Error getting windows: {e}")
        return []


def _cycle_window(direction: int):
    active_app = ui.active_app()
    if not active_app:
        print("[sleep_window] No active application.")
        return

    windows = _get_app_windows(active_app)
    print(f"[sleep_window] Active app: {active_app.name!r}, found {len(windows)} windows")

    if len(windows) <= 1:
        # Fallback to standard OS shortcut in case Talon UI accessibility missed a window
        print("[sleep_window] <= 1 window detected via UI, sending macOS shortcut")
        if direction > 0:
            actions.key("cmd-`")
        else:
            actions.key("cmd-shift-`")
        return

    active_win = ui.active_window()
    try:
        current_idx = windows.index(active_win)
        next_idx = (current_idx + direction) % len(windows)
    except Exception:
        next_idx = 0

    target = windows[next_idx]
    print(
        f"[sleep_window] Switching from {getattr(active_win, 'title', 'unknown')!r} "
        f"to {target.title!r} (index {next_idx + 1}/{len(windows)})"
    )
    try:
        target.focus()
    except Exception as e:
        print(f"[sleep_window] Failed target.focus(): {e}, falling back to key shortcut")
        if direction > 0:
            actions.key("cmd-`")
        else:
            actions.key("cmd-shift-`")


@mod.action_class
class Actions:
    def sleep_window_next():
        """Focus next window of active application, working in all modes."""
        _cycle_window(1)

    def sleep_window_previous():
        """Focus previous window of active application, working in all modes."""
        _cycle_window(-1)
