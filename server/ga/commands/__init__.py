from . import import_history


def init_commands(app):
    app.cli.add_command(import_history.import_history)
    app.cli.add_command(import_history.update_history)
