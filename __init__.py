import os
import json

import sublime
import sublime_plugin


CONTEXT_MENU = 0
WIDGET_MENU  = 1


class DynamicMenu():
    __slot__ = ['file', 'registers']

    def __init__(self, file):
        self.file = file
        self.registers = {}

# side bar dynamic menu is unsupported
context_dynamic_menu = DynamicMenu('Context.sublime-menu')
widget_dynamic_menu  = DynamicMenu('Widget Context.sublime-menu')

all_dynamic_menu = [
    context_dynamic_menu,
    widget_dynamic_menu
]


def register(name, make, kind=CONTEXT_MENU):
    all_dynamic_menu[kind].registers[name]= make

def item(caption, command, args):
    return {'caption': caption, 'command': command, 'args': args}

def line(id):
    return { 'caption': '-', 'id': id }

def fold_items(caption, items):
    return {'caption': caption, 'children': items}

def write_menu(menu, filepath):
    print('file: ', filepath)
    print('menu:', menu)
    with open(filepath, 'w+') as file:
        json.dump(menu, file)

def plugin_loaded():
    menus_cache_dir = os.path.join(sublime.cache_path(), 'dctxmenu')
    os.makedirs(menus_cache_dir, exist_ok=True)
    for dyn_menu in all_dynamic_menu:
        dyn_menu.file = os.path.join(menus_cache_dir, dyn_menu.file)
        write_menu([], dyn_menu.file)

def plugin_unloaded():
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
