from talon import Context

ctx = Context()
ctx.matches = "os: mac"

try:
    @ctx.action("user.noise_trigger_pop")
    def on_pop():
        """No-op override to prevent community pop handling from interfering with Parrot."""
        pass
except Exception:
    pass
