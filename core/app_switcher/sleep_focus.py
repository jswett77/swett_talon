from talon import Module, actions, ui, app

mod = Module()

APP_MAPPINGS = {
    "chrome": ["Google Chrome", "Chrome"],
    "chat": ["Google Chat"],
    "term": ["iTerm2", "iTerm", "Terminal"],
    "remote": ["Chrome Remote Desktop"],
    "mail": ["Gmail", "Mail"],
    "calendar": ["Google Calendar", "Calendar"],
}

@mod.action_class
class Actions:
    def sleep_focus_app(name: str):
        """Focus a preferred application even when speech is disabled"""
        targets = APP_MAPPINGS.get(name.lower(), [name])
        running = {a.name: a for a in ui.apps(background=False)}

        for target in targets:
            if target in running:
                actions.user.switcher_focus_app(running[target])
                return

        # Fallback to standard switcher_focus if not found in ui.apps directly
        for target in targets:
            try:
                actions.user.switcher_focus(target)
                return
            except Exception:
                pass

        app.notify(f"App not running: {name}")
