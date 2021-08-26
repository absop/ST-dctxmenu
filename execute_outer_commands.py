import os
import subprocess
import dctxmenu

import sublime
import sublime_plugin


user_settings = 'ExecuteOuterCommands.sublime-settings'

def plugin_loaded():
    def load_user_settings():
        plugin = ExecuteOuterCommandsCommand
        plugin.caption = settings.get('caption', 'Execute Outer Commands')
        plugin.commands = settings.get('commands', [])

    settings = sublime.load_settings(user_settings)
    settings.clear_on_change('caption')
    settings.add_on_change('caption', load_user_settings)

    load_user_settings()

    sublime.set_timeout(
        lambda: dctxmenu.register(__package__,
            ExecuteOuterCommandsCommand.make_menu),
        500
    )

def plugin_unloaded():
    dctxmenu.deregister(__package__)


class ExecuteOuterCommandsCommand(sublime_plugin.WindowCommand):
    executor = 'execute_outer_commands'
    caption  = 'Execute Outer Commands'
    commands = []

    @classmethod
    def make_menu(cls, view, event):
        if not os.path.exists(view.file_name() or ''):
            return None
        items = []
        for cmd in cls.commands:
            enabled = cmd.get('enabled', True)
            if not enabled:
                continue
            command = cmd.get('command', '')
            caption = cmd.get('caption', '') or str(command)
            if caption and command:
                items.append(dctxmenu.item(caption, cls.executor, cmd))

        if len(items) == 0:
            return None
        elif len(items) == 1:
            return items[0]
        else:
            return dctxmenu.fold_items(cls.caption, items)

    def is_valid_command(self, command):
        isstr = lambda x: isinstance(x, str)
        return (isinstance(command, list) and all(map(isstr, command)) or
                isinstance(command, str))

    def run(self, command, shell=True, **kwargs):
        if not self.is_valid_command(command):
            sublime.error_message('Invalid command: ' + str(command))
            return
        variables = self.window.extract_variables()
        cmd = sublime.expand_variables(command, variables)
        if shell and type(cmd) is list:
            cmd = ' '.join(cmd)
        try:
            subprocess.Popen(cmd, shell=shell)
        except Exception as e:
            errmsg = 'Error occurred when execute outer command: ' + str(command)
            sublime.status_message(errmsg)
