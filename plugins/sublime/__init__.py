from sublime_plugin import WindowCommand, TextCommand
import sublime

__all__ = ['ST2', 'ST3', 'WindowAndTextCommand', 'Settings', 'FileSettings']

ST2 = sublime.version().startswith('2')
ST3 = not ST2


class WindowAndTextCommand(WindowCommand, TextCommand):
    """A class to derive from when using a Window- and a TextCommand in one
    class (e.g. when you make a build system that should/could also be called
    from the command palette with the view in its focus).

    Defines both self.view and self.window.

    Be careful that self.window may be ``None`` when called as a
    TextCommand because ``view.window()`` is not really safe and will
    fail in quite a few cases. Since the compromise of using
    ``sublime.active_window()`` in that case is not wanted by every
    command I refused from doing so. Thus, the command's on duty to check
    whether the window is valid.

    Since this class derives from both Window- and a TextCommand it is also
    callable with the known methods, like
    ``window.run_command("window_and_text")``.
    I defined a dummy ``run`` method to prevent parameters from raising an
    exception so this command call does exactly nothing.
    Still a better method than having the parent class (the command you
    will define) derive from three classes with the limitation that this
    class must be the first one (the *Command classes do not use super()
    for multi-inheritance support; neither do I but apparently I have
    reasons).
    """
    def __init__(self, param):
        # no super() call! this would get the references confused
        if isinstance(param, sublime.Window):
            self.window = param
            self._window_command = True  # probably called from build system
            self.typ = WindowCommand
        elif isinstance(param, sublime.View):
            self.view   = param
            self._window_command = False
            self.typ = TextCommand
        else:
            raise TypeError("Something really bad happened and you are responsible")

        self._update_members()

    def _update_members(self):
        if self._window_command:
            self.view = self.window.active_view()
        else:
            self.window = self.view.window()

    def run_(self, *args):
        """Wraps the other run_ method implementations from sublime_plugin.
        Required to update the self.view and self.window variables.
        """
        self._update_members()
        # Obviously `super` does not work here
        self.typ.run_(self, *args)


class Settings(object):
    """Helper class for accessing sublime.Settings' values.

        Settings(settings, none_erases=False)

            * settings (sublime.Settings)
                Should be self-explanatory.

            * none_erases (bool, optional)
                Iff ``True`` a setting's key will be erased when setting it to
                ``None``. This only has a meaning when the key you erase is
                defined in a parent Settings collection which would be
                retrieved in that case.

        Defines the default methods for sublime.Settings:

            get(key, default=None)
            set(key, value)
            erase(key)
            has(key)
            add_on_change(key, on_change)
            clear_on_change(key, on_change)

            http://www.sublimetext.com/docs/2/api_reference.html#sublime.Settings

        If ``none_erases == True`` you can erase a key when setting it to
        ``None``. This only has a meaning when the key you erase is defined in
        a parent Settings collection which would be retrieved in that case.

        The following methods can be used to retrieve a setting's value:

            value = self.get('key', default)
            value = self['key']
            value = self.key_without_spaces

        The following methods can be used to set a setting's value:

            self.set('key', value)
            self['key'] = value
            self.key_without_spaces = value

        The following methods can be used to erase a key in the setting:

            self.erase('key')
            self.set('key', None) or similar  # iff ``none_erases == True``
            del self.key_without_spaces

      ! Important:
        Don't use the attribute method with one of these keys; ``dir(Settings)``:

            ['__class__', '__delattr__', '__dict__', '__doc__', '__format__',
            '__getattr__', '__getattribute__', '__getitem__', '__hash__',
            '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__',
            '__repr__', '__setattr__', '__setitem__', '__sizeof__', '__str__',
            '__subclasshook__', '__weakref__',

            '_none_erases', '_s', '_settable_attributes',

            'add_on_change', 'clear_on_change',
            'erase', 'get', 'has', 'set']

        Getting will return the respective function/value, setting will do
        nothing. Setting of _leading_underline_values from above will result in
        unpredictable behavior. Please don't do this! And re-consider even when
        you know what you're doing.
    """
    _none_erases = False
    _s           = None
    _settable_attributes = ('_s', '_none_erases')  # allow only setting of these attributes

    def __init__(self, settings, none_erases=False):
        if not isinstance(settings, sublime.Settings):
            raise ValueError("Not an instance of sublime.Settings")
        self._s = settings
        self._none_erases = none_erases

    def get(self, key, default=None):
        """Returns the named setting, or ``default`` if it's not defined.
        """
        return self._s.get(key, default)

    def set(self, key, value):
        """Sets the named setting. Only primitive types, lists, and
        dictionaries are accepted.
        Erases the key iff ``value is None``.
        """
        if value is None and self._none_erases:
            self.erase(key)
        else:
            self._s.set(key, value)

    def erase(self, key):
        """Removes the named setting. Does not remove it from any parent Settings.
        """
        self._s.erase(key)

    def has(self, key):
        """Returns true iff the named option exists in this set of Settings or
        one of its parents.
        """
        return self._s.has(key)

    def add_on_change(self, key, on_change):
        """Register a callback to be run whenever the setting with this key in
        this object is changed.
        """
        self._s.add_on_change(key, on_change)

    def clear_on_change(self, key, on_change):
        """Remove all callbacks registered with the given key.
        """
        self._s.clear_on_change(key, on_change)

    def __getitem__(self, key):
        """self[key]"""
        return self.get(key)

    def __setitem__(self, key, value):
        """self[key] = value"""
        self.set(key, value)

    def __getattr__(self, key):
        """self.key_without_spaces"""
        return self.get(key)

    def __setattr__(self, key, value):
        """self.key_without_spaces = value"""
        if key in self._settable_attributes:
            object.__setattr__(self, key, value)
        else:
            self.set(key, value)

    def __delattr__(self, key):
        """del self.key_without_spaces"""
        if key in dir(self):
            return
        else:
            self.erase(key)


class FileSettings(Settings):
    """Helper class for accessing sublime.Settings' values.

        Derived from sublime_lib.Settings. Please also read the documentation
        there.

        FileSettings(name, none_erases=False)

            * name (str)
                The file name that's passed to sublime.load_settings().

            * none_erases (bool, optional)
                Iff ``True`` a setting's key will be erased when setting it to
                ``None``. This only has a meaning when the key you erase is
                defined in a parent Settings collection which would be
                retrieved in that case.

        Defines the following extra methods:

            save()
                Flushes in-memory changes to the disk

                See: sublime.save_settings(name)

        Adds these attributes to the list of unreferable attribute names for
        settings:

            ['_name', 'save']

        Please compare with the list from sublime_lib.Settings or
        ``dir(FileSettings)``.
    """
    _name = ""
    _settable_attributes = ('_s', '_name', '_none_erases')  # allow only setting of these attributes

    def __init__(self, name, none_erases=False):
        settings = sublime.load_settings(name)
        if not settings:
            raise ValueError('Could not create settings from name "%s"' % name)
        self._name = name
        super(FileSettings, self).__init__(settings, none_erases)

    def save(self):
        sublime.save_settings(self._name)
