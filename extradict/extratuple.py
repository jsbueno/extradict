import sys



def namedtuple(name, attrs):
    """
    Alternate implementation to stdlib's 'namedtuple" that does not
    make use of "eval" at runtime.

    Instead, it relies on closures to do its magic.

    """
    if isinstance(attrs , str):
        attrs = attrs.split()
    attrs = tuple(attrs)

    _field_order  = {field: i for i, field in enumerate(attrs)}

    class NamedTuple(tuple):
        def __getattribute__(self, attr):
            n = _field_order.get(attr, None)
            if n is not None:
                return self[n]
            return tuple.__getattribute__(self, attr)

        def __new__(cls, *args, **kw):
            if len(args) + len(kw) != len(attrs):
                # to replicate the exact collections.namedtuple error messages here  mean to duplicate
                # Python's argument parsing logic itself. A meaningful TypeError should suffice
                # raise TypeError("__new__() missing {} required positional argument{}: {}")
                raise TypeError("__new__() got an incorrect number of parameters for '{}'".format(name))
            if kw:
                original = args
                args = list(args) + [None] * len(kw)
                for key, value in kw.items():
                    pos = _field_order.get(key, None)
                    if pos is None:
                        raise TypeError("__new__() got an unexpected keyword argument '{}'".format(key))
                    if pos < len(original):
                        raise TypeError("__new__() got multiple values for argument '{}'".format(key))
                    args[pos] = value
            return tuple.__new__(cls, args)

        def __repr__(self):
            return "{}({})".format(self.__class__.__name__, ", ".join("{}={}".format(name, value) for name, value in zip(self._fields, self)))

        def _asdict(self):
            from collections import OrderedDict
            return OrderedDict((key, value) for key, value in zip(self._fields, self))

        _fields = __definition_order__ = attrs

    NamedTuple.__name__ = name
    NamedTuple.__qualname__ = ".".join((sys._getframe().f_back.f_globals.get("__name__"), name))

    return NamedTuple
    #dct = {
        #"__new__": __new__,
        #"__slots__": (),
        #"__getattribute__": __getattribute__,
        #"_fields": attrs,
        #"__repr__":__repr__,
        #"__definition_order__": attrs,
        #"_asdict": _asdict
    #}
    #return type(name, (tuple,), dct)


def fastnamedtuple(name, attrs):
    """
    Like namedtuple but the class returned take an iterable for its values
    rather than positioned or named parameters. No checks are made towards the iterable
    lenght, which should match the number of attributes
    It is faster for instantiating as compared with stdlib's namedtuple
    """
    cls = namedtuple(name, attrs)
    delattr (cls, "__new__")
    cls.__qualname__ = ".".join((sys._getframe().f_back.f_globals.get("__name__"), name))
    return cls