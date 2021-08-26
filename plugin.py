import os
import json

import sublime
import sublime_plugin


class DynamicMenu():
    __slot__ = ['file', 'registers']

    def __init__(self, file):
        self.file = file
        self.registers = {}


# side bar dynamic menu is unsupported
CONTEXT_MENU = 0
WIDGET_MENU  = 1

all_dynamic_menu = [
    DynamicMenu('Context.sublime-menu'),
    DynamicMenu('Widget Context.sublime-menu')
]

def validate_menu_kind(kind):
    if not (kind < len(all_dynamic_menu)):
        raise ValueError("%d is not a valid menu kind" % kind)

def register(name, make, kind=CONTEXT_MENU):
    validate_menu_kind(kind)
    all_dynamic_menu[kind].registers[name] = make

def deregister(name, kind=CONTEXT_MENU):
    validate_menu_kind(kind)
    all_dynamic_menu[kind].registers.pop(name)

def item(caption, command, args):
    return {'caption': caption, 'command': command, 'args': args}

def line(id):
    return {'caption': '-', 'id': id}

def fold_items(caption, items):
    return {'caption': caption, 'children': items}

def write_menu(menu, filepath):
    with open(filepath, 'w+') as file:
        json.dump(menu, file)


def plugin_loaded():
    menus_cache_dir = os.path.join(sublime.cache_path(), 'dctxmenu')
    os.makedirs(menus_cache_dir, exist_ok=True)
    for dyn_menu in all_dynamic_menu:
        dyn_menu.file = os.path.join(menus_cache_dir, dyn_menu.file)
        write_menu([], dyn_menu.file)
    try:
        for kind, dyn_menu in sublime.dctxmenu_temp_data():
            for name, make in dyn_menu.registers.items():
                register(name, make, kind)
    except:
        pass

def plugin_unloaded():
    import time
    _deadline = time.time() + 1.0
    _all_dynamic_menu = all_dynamic_menu
    sublime.dctxmenu_temp_data = lambda: (
        enumerate(_all_dynamic_menu if time.time() < _deadline else []))
    try:
        for dyn_menu in all_dynamic_menu:
            os.remove(dyn_menu.file)
    except:
        pass


class DynamicContextMenuEventListener(sublime_plugin.EventListener):
    def on_post_text_command(self, view, command, args):
        if command == 'context_menu':
            for dyn_menu in all_dynamic_menu:
                write_menu([], dyn_menu.file)

    def on_text_command(self, view, command, args):
        if command == 'context_menu' and args and 'event' in args:
            event = args['event']
            for dyn_menu in all_dynamic_menu:
                items = []
                for name, make in dyn_menu.registers.items():
                    item = make(view, event)
                    if   isinstance(item, dict):
                        items.append(item)
                    elif isinstance(item, list):
                       items.extend(item)
                if items:
                    write_menu(items, dyn_menu.file)
