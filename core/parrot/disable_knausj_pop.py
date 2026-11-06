from talon import Context, Module

mod = Module()


@mod.action_class
class Actions:
    def noise_trigger_pop():
        """Called when a pop noise is made."""
        pass


ctx = Context()


@ctx.action("user.noise_trigger_pop")
def on_pop():
    """No-op to prevent knausj pop click from interfering with Parrot."""
    pass
