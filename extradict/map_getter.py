import sys
import threading
import contextvars
import dis, sys, inspect
import itertools

_sentinel = object()


class _PseudoModule(object):
    def __init__(self, mapping, default=_sentinel):
        try:
            self.__dict__ = mapping
        except TypeError:
            self._obj = mapping
        else:
            self._obj = _sentinel
        self._default = default

    def getlines(self, file):
        return ""

    def __getattr__(self, attr):
        if self._obj is not _sentinel:
            try:
                return getattr(self._obj, attr)
            except AttributeError:
                if self._default is _sentinel:
                    raise AttributeError(
                        f"Object '{type(self._obj)}' has no attribute '{attr}' "
                    )
        if self._default is _sentinel:
            # Try to extract a value from mapping, which could be a
            # defaultdict or some similar mapping:
            try:
                value = self.__dict__[attr]
            except KeyError:
                raise AttributeError(
                    f"Mapping '{type(self.mapping)}' has no '{attr}' key"
                )
            return value
        if not callable(self._default):
            return self._default
        try:
            value = self._default(attr)
        except TypeError:
            # try default dict style argumentless default factory:
            value = self._default()
        return value


class MapGetter(object):
    """
    A context manager to allow one to "import" variables from a mapping or
    factory function. This helps preserve DRY principle:

    # Example:
    >>> a = dict(b=1, c=2)
    >>> with MapGetter(a) as blah:
    ...    from blah import b, c

    >>> print((b, c))
    (1, 2)

    It is intesresting to note that it will work for ordinary attributes
    from Python objects, and, as well, for constant names inside a Python
    enum.Enum class. That may be the major use case of this:

    In[1]: import enum
    In [2]: from extradict import MapGetter

    In 43]: class Colors(enum.Enum):
        ...:     RED = 1, 0, 0
        ...:     GREEN = 0, 1, 0
        ...:     BLUE = 0, 0, 1
        ...:

    In [4]: with MapGetter(Colors):
        ...:     from Colors import RED, GREEN, BLUE
        ...:

    In [5]: RED, GREEN, BLUE
    Out[5]: (<Colors.RED: (1, 0, 0)>, <Colors.GREEN: (0, 1, 0)>, <Colors.BLUE: (0, 0, 1)>)


    """

    def __init__(self, mapping=None, default=_sentinel):
        if mapping is None and default is _sentinel:
            raise TypeError(
                "MapGetter must be called with at least one of mapping or default (value/factory function)"
            )
        self.builtins = (
            __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        )
        self.mapping = mapping if mapping is not None else {}
        self.default = default

    def __enter__(self):
        self.original_import = self.builtins["__import__"]
        self.builtins["__import__"] = self._map_getter
        self._thread = threading.current_thread()
        return self.mapping

    def _map_getter(self, name, globals_, locals_, from_list, level=-1):
        # "from_list" gets the names wanted in the "import ... from ... " statement,
        # however, they are not actually expected to be returned.
        # the fact the remainer of the import machinery does not use them
        # makes it worth to keep this implementation using a __import__ monkey patch -
        # no other func gets "from_list" and all the machinery expects the actual
        # module to be created on sys.modules - which we don't want.

        # FIXME: Make this asyncio safe as well.
        # (May wait for Python 3.7 with PEP-555 implemented)
        if (
            threading.current_thread() != self._thread
            or sys._getframe().f_back.f_locals.get(name, None) is not self.mapping
        ):
            return self.original_import(name, globals_, locals_, from_list, level)
        return _PseudoModule(self.mapping, self.default)

    def __exit__(self, type, value, traceback):
        self.builtins["__import__"] = self.original_import
        return False



class Extractor:
    instances = {}
    def __new__(cls, source):
        frame = sys._getframe()
        while True:
            frame = frame.f_back
            # Skip debugger frames if any -
            if not frame.f_globals["__file__"].endswith(("pdb.py", "gdb,py")):
                break
        # Maybe we could replace ourselves in the frame for an instance?
        file, lineno = id = frame.f_globals.get("__file__"), frame.f_lineno
        if id not in cls.instances:
            instance = cls.instances[id] = super().__new__(cls)
            instance._get_targets(frame)
            # do not create constextvars that won't be used.
            if len(instance.targets) > 1:
                instance.target_iterator = contextvars.ContextVar("target_iterator", default=None)
                instance.source = contextvars.ContextVar("source", default=None)
        else:
            instance = cls[instances[id]]

        if len(instance.targets) == 1:
            return instance._get_item_or_attr(source, instance.targets[0])

        instance.source.set(source)
        #if there is mote than one attr to extract,
        #Python will call __getitem__ once for each target:
        return instance

    def _get_targets(self, frame):
        targets = []
        f = frame
        # in python 3.13, the line number can be fetched with instruction.line_number, directly.
        line_number = f.f_lineno



        instructions =  dis.get_instructions(f.f_code, first_line=f.f_code.co_firstlineno)
        instructions = list(itertools.takewhile(
            lambda instr: (not instr.positions) or (not instr.positions.lineno) or instr.positions.lineno <= line_number,
            (instr for instr in dis.get_instructions(f.f_code, first_line=f.f_code.co_firstlineno) if not instr.positions or not instr.positions.lineno or instr.positions.lineno>=line_number)
        ))

        index = -1
        while True:
            if instructions[index].opname in ("CALL", "CALL_KW", "CALL_FUNCTION_EX"):
                break
            index -= 1
        else:
            raise RuntimeError("Could not resolve Extractor targets")

        # good for debugging:
        #x1 = [(i.opname, i.argval) for i in instructions]
        for instruction  in instructions[index:]:

            if "STORE_" not in instruction.opname:  # STORE_FAST_STORE_FAST, STORE_FAST, STORE_GLOBAL, STORE_NAME, STORE_DEREF
                continue
            if isinstance(argval:=instruction.argval, tuple):  # STORE_FAST_STORE_FAST
                targets.extend(argval)
            else:
                targets.append(argval)
        self.targets = targets


    def _get_targets_using_source(self, frame):
        # FIXME: this is less capable than the assembler based version -
        # as it doesn't support an statement broken into multiple lines.
        f = frame
        source = inspect.getsource(f.f_code)
        assign_line = source.split("\n")[f.f_lineno - f.f_code.co_firstlineno]
        targets_str = assign_line.split("=")[0]
        self.targets = [target.strip() for target in targets_str.split(",")]


    if sys.version_info < (3,11):
        _get_targets = _get_targets_using_source

    def _get_item_or_attr(self, source,  name):
        try:
            value = source.__getitem__(name)
        except (KeyError, AttributeError, TypeError) :
            value = getattr(source, name)
        return value


    def __len__(self):
        return len(self.targets)

    def __getitem__(self, index):
        # xx = [instruction for instruction in dis.get_instructions(frame.f_code, first_line=frame.f_code.co_firstlineno)]
        values = []
        if not (targets:=self.target_iterator.get()):
            self.target_iterator.set(targets:=iter(self.targets))
        target_name = next(targets, None)
        if target_name is None:
            self.target_iterator.set(None)
            self.source.set(None)
            raise IndexError()
        return self._get_item_or_attr(self.source.get(), target_name)

