# edit.py, courtesy of @lunixbochs (https://github.com/lunixbochs)
# and slightly modified
# modified as well by @rageandqq
"""Abstraction for edit objects in ST3

All methods on "edit" create an edit step. When leaving the `with` block, all
the steps are executed one by one.

Be careful: All other code in the with block is still executed! If a method on
edit depends on something you do based on a previous method on edit, you
should use the second method. However, using `edit.callback` or pass a
function as an argument you can circumvent that if it's only small things. The
function will be called with the parameters `view` and `edit` when processing
the edit group.

Usage 1:
    with Edit(view) as edit:
        edit.insert(0, "text")
        edit.replace(reg, "replacement")
        edit.erase(lambda v,e: sublime.Region(0, v.size()))
        # OR
        # edit.callback(lambda v,e: v.erase(e, sublime.Region(0, v.size())))

Usage 2:
    def do_ed(view, edit):
        edit.erase()
        view.insert(edit, 0, "text")
        view.sel().clear()
        view.sel().add(sublime.Region(0, 4))
        edit.replace(reg, "replacement")

    Edit.call(do_ed)

Available methods:
    Note: Any of these parameters can be a function which will be called with
    (optional) parameters `view` and `edit` when processing the edit group.
    Example callbacks:
        `lambda: 1`
        `lambda v: v.size()`
        `lambda v, e: v.erase(e, reg)`

    insert(point, string)
        view.insert(edit, point, string)

    append(point, string)
        view.insert(edit, view.size(), string)

    erase(region)
        view.erase(edit, region)

    replace(region, string)
        view.replace(edit, region, string)

    callback(func)
        func(view, edit)

"""

import inspect
import sublime
import sublime_plugin

try:
    sublime.edit_storage
except AttributeError:
    sublime.edit_storage = {}


def run_callback(func, *args, **kwargs):
    spec = inspect.getfullargspec(func)

    args = args[:len(spec.args) or 0]
    if not spec.varargs:
        kwargs = {}

    return func(*args, **kwargs)


class EditStep:
    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.args = args

    def run(self, view, edit):
        if self.cmd == 'callback':
            return run_callback(self.args[0], view, edit)

        funcs = {
            'insert':  view.insert,
            'erase':   view.erase,
            'replace': view.replace,
        }
        func = funcs.get(self.cmd)
        if func:
            args = self.resolve_args(view, edit)
            func(edit, *args)

    def resolve_args(self, view, edit):
        args = []
        for arg in self.args:
            if callable(arg):
                arg = run_callback(arg, view, edit)
            args.append(arg)
        return args


class Edit:
    def __init__(self, view, func=None):
        self.view = view
        self.steps = []

    def __nonzero__(self):
        return bool(self.steps)

    __bool__ = __nonzero__  # Python 3 equivalent

    def step(self, cmd, *args):
        step = EditStep(cmd, *args)
        self.steps.append(step)

    def insert(self, point, string):
        self.step('insert', point, string)

    def append(self, string):
        # import spdb ; spdb.start()
        self.step('insert', lambda v: v.size(), string)

    def erase(self, region):
        self.step('erase', region)

    def replace(self, region, string):
        self.step('replace', region, string)

    @classmethod
    def call(cls, view, func):
        if not (func and callable(func)):
            return

        with cls(view) as edit:
            edit.callback(func)

    def callback(self, func):
        self.step('callback', func)

    def run(self, view, edit):
        for step in self.steps:
            step.run(view, edit)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        view = self.view
        key = str(hash(tuple(self.steps)))
        sublime.edit_storage[key] = self
        view.run_command('sl_apply_edit', {'key': key})


# Changed command name to not clash with other variations of this file
class SlApplyEdit(sublime_plugin.TextCommand):
    def run(self, edit, key):
        sublime.edit_storage.pop(key).run(self.view, edit)


# Make command known to sublime_command despite not being loaded by it
sublime_plugin.text_command_classes.append(SlApplyEdit)

# Make the command unloadable
plugins = [SlApplyEdit]
