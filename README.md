# dctxmenu (Dynamic Context Menu)
[中文文档](README.cn.md)

[dctxmenu](https://github.com/absop/dctxmenu) is a Sublime Text plugin, which support dynamic context menu (right-click menu).

By modifying the settings file, users can bind **external commands** to right-click menu items or shortcuts, so that the corresponding external commands can be executed easily with the right mouse button or shortcuts.


# Installation
- Use `git clone` to download the repository into your `Sublime Text package directory` (this requires you to have Git installed on your computer).

- Download the repository archive directly from the GitHub web page and extract it to your `Sublime Text package directory`. Be sure to change the directory name to `dctxmenu` and `dctxmenu` should contain the source code files directly without unnecessary nestings, as follows
   ```
   dctxmenu
       Default.sublime-commands
       Default.sublime-keymap
       ExecuteOuterCommands.sublime-settings
       execute_outer_commands.py
       LICENSE
       Main.sublime-menu
       plugin.py
       README.md
       __init__.py
   ```


# Bind External Commands to The Right-click Menu
You can using the command palette to type and execute the command `Preferences ExecuteOutterCommands Settings`, or click on the main menu (Preferences>Package Settings> dctxmenu >Settings), to begin editing the settings.

You can add a **menu sub-item** to the right-click menu by adding a **command-map** to the `commands` entry, which is one of the two setting entires of this plugin, the other is `caption`.

Here's an example
```json
{
    "caption": "Execute Outer Commands",

    "commands": [
        {
            "caption": "WSL Here",
            "command": ["ConEmu.exe", "/dir", "\"${file_path}\""],
        },
        {
            "caption": "Cmder Here",
            "command": ["Cmder.exe", "\"${file_path}\""]
        }
    ]
}
```
Where `commands` is a list of `command-map`s.

Each `command-map` is a dictionary (Dict, or Map), where `caption` is the title of the corresponding command displayed in the menu, and `command` is the specific command to be executed. Please refer to the above example to fill in carefully. `command` can be a string, or a list of strings, the strings of `command` can contain some variables (reference [Sublime Text API documentation](https://www.sublimetext.com/docs/api_reference.html#ver-dev), search `extract_variables`) and these variables will be replaced with their corresponding values when the command is executed.

In addition, `command-map` supports a optional argument called `shell` with a boolean value, which defaults to `true` and is passed to `subprocess` and is not normally used.

An entry in `commands` directly corresponds to a menu item. When there are multiple menu items, the menu will be folded and the folded menu will be titled with the value of the `caption` of the same level as `commands`. When there is only one `command-map` in `commands`, only one top-level menu is added to the right-click menu.

The following screen-shot shows the two menu sub-items were added to the right-click menu with using the example settings above.
![](images/multi-items.png)

Here's another example
- The settings
   ```json
   {
       "commands": [
           {
               "caption": "Cmder Here",
               "command": ["Cmder.exe", "\"${file_path}\""]
           }
       ]
   }
   ```
- A screen-shot of the corresponding menu
   ![](images/single-item.png)


# Binding Shortcuts
By editing your personal `keymap` file (Preferences>Key Bindings), you can also bind specific external commands to shortcuts, so that you can use shortcuts to execute external commands in Sublime Text. Here's an example
```json
[
    {
        "keys": ["ctrl+alt+t"],
        "command": "execute_outer_commands",
        "args": {
            "command": ["Cmder.exe", "\"${file_path}\""],
            "shell": true
        }
    }
]
```
You can copy this example and modify the `"keys"` and `"args"` entries. The value of `"args"` is a `command-map`, except that the `caption` entry will be ignored.


# Advanced usage
Register & use the features of `dctxmenu` in another plugin
```python
import dctxmenu

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
```
Other plugins can use `dctxmenu`'s function by registering a menu-generating function (Such as the above `ExecuteOuterCommandsCommand.make_menu`).

For details, please read the source code of the `dctxmenu` core support library (the [plugin.py](plugin.py) file in this repository (80 lines)) and refer to its use example: the [execute_outer_commands.py](execute_outer_commands.py) file (functional part of this plugin, less than 75 lines). Here are some more examples

- [SearchOnline](https://github.com/absop/SearchOnline)
- [OpenOtherFiles](https://github.com/absop/OpenOtherFiles)
- [Translators](https://github.com/absop/Translators)
