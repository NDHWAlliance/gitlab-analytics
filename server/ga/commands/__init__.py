from . import import_history
from . import hook


def init_commands(app):
    app.cli.add_command(import_history.import_history)
    app.cli.add_command(import_history.update_history)
    app.cli.add_command(hook.hook_all)
    #app.cli.add_command(import_history.test)
