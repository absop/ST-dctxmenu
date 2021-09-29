import os
import json
import time
import webbrowser

import sublime
import sublime_plugin


all_menu_creater_classes = {}
need_reload = True


def register(modulename, subclass):
    all_menu_creater_classes[modulename] = subclass
    if subclass not in MenuCreater.__subclasses__():
        sublime.set_timeout_async(
            lambda: sublime_plugin.reload_plugin(modulename),
            100)


def remove(modulename):
    all_menu_creater_classes.pop(modulename, '')
    if need_reload:
        sublime_plugin.reload_plugin(__name__)


def plugin_loaded():
    global all_menu_writers
    all_menu_writers = []
    cache_path = os.path.join(sublime.cache_path(), 'dctxmenu')
    os.makedirs(cache_path, exist_ok=True)
    for hook, file in [
            ('context_menu', 'Context.sublime-menu'),
            ('widget_context_menu', 'Widget Context.sublime-menu')
        ]:
        writer = MenuWriter(hook, os.path.join(cache_path, file))
        all_menu_writers.append(writer)
    try:
        global need_reload
        need_reload = False
        for modulename in sublime.dctxmenu_temp_data():
            sublime_plugin.reload_plugin(modulename)
        need_reload = True
    except:
        pass


def plugin_unloaded():
    modulenames = list(all_menu_creater_classes.keys())
    _deadline = time.time() + 1.0
    sublime.dctxmenu_temp_data = (
        lambda: modulenames if time.time() < _deadline else []
    )


class MenuCreater:
    def __init__(self, view):
        self.view = view

    def item(self, caption, command, args):
        return {'caption': caption, 'command': command, 'args': args}

    def line(self, id=''):
        if not id:
            return {'caption': '-'}
        return {'caption': '-', 'id': id}

    def folded_item(self, caption, children):
        return {'caption': caption, 'children': children}

    def context_menu(self, event):
        raise NotImplementedError

    def widget_context_menu(self, event):
        raise NotImplementedError


class MenuWriter:
    __slots__ = ['hook', 'path', 'items']

    def __init__(self, hook, path):
        self.hook = hook
        self.path = path
        self.clear()

    def clear(self):
        self.items = []
        self.write()

    def write(self):
        with open(self.path, 'w+') as fd:
            json.dump(self.items, fd)

    def save(self):
        if self.items:
            self.write()

    def record(self, obj, event):
        try:
            make_item = getattr(obj, self.hook)
            item = make_item(event)
            if isinstance(item, dict):
                self.items.append(item)
            elif isinstance(item, list):
                self.items.extend(item)
        except:
            pass


class ContextMenuWriterEventListener(sublime_plugin.EventListener):
    def on_post_text_command(self, view, command, args):
        if command == 'context_menu':
            for writer in all_menu_writers:
                writer.clear()

    def on_text_command(self, view, command, args):
        if command == 'context_menu' and args and 'event' in args:
            event = args['event']
            for cls in MenuCreater.__subclasses__():
                try:
                    creater = cls(view)
                except Exception as e:
                    sublime_plugin._instantiation_error(cls, e)
                else:
                    for writer in all_menu_writers:
                        writer.record(creater, event)

            for writer in all_menu_writers:
                writer.save()


class OpenFileWithDefaultApplicationCommand(sublime_plugin.WindowCommand):
    def run(self, file):
        webbrowser.open_new_tab(file)
