# Extra Dictionary classes and utilities for Python

New utilities to be added as they are devised


## VersionDict

A Python Mutable Mapping Container (dictionary :-) ) that
can "remember" previous values.
Use it wherever you would use a dict - at each
key change or update, it's `version` attribute
is increased by one.

### Special and modified methods:

`.get` method is modified to receive an optional
named  `version` parameter that allows one to retrieve
for a key the value it contained at that respective version.
NB. When using the `version` parameter, `get` will raise
a KeyError if the key does not exist for that version and
no default value is specified.

`.copy(version=None)`:  yields a copy of the current dictonary at that version, with history preserved
(if version is not given, the current version is used)

`.freeze(version=None)` yields a snapshot of the versionDict in the form of a plain dictionary for
the specified version


### Implementation:
It works by internally keeping a list of (named)tuples with
(version, value) for each key.


### Example:

```

>>> from extradict import VersionDict
>>> a = VersionDict(b=0)
>>> a["b"] = 1
>>> a["b"]
1
>>> a.get("b", version=0)
0
```

For extra examples, check the "tests" directory

## OrderedVersionDict

Inherits from VersionDict, but preserves and retrieves key
insertion order. Unlike a plain "collections.OrderedDict",
however, whenever a key's value is updated, it is moved
last on the dictionary order.

### Example:
```
>>> from collections import OrderedDict
>>> a = OrderedDict((("a", 1), ("b", 2), ("c", 3)))
>>> list(a.keys())
>>> ['a', 'b', 'c']
>>> a["a"] = 3
>>> list(a.keys())
>>> ['a', 'b', 'c']

>>> from extradict import OrderedVersionDict
>>> a = OrderedVersionDict((("a", 1), ("b", 2), ("c", 3)))
>>> list(a.keys())
['a', 'b', 'c']
>>> a["a"] = 3
>>> list(a.keys())
['b', 'c', 'a']
```

## MapGetter
A Context manager that allows one to pick variables from inside a dictionary,
mapping, or any Python object by using the  `from <myobject> import key1, key2` statement.



```
>>> from extradict import MapGetter
>>> a = dict(b="test", c="another test")
>>> with MapGetter(a) as a:
...     from a import b, c
...
>>> print (b, c)
test another test
```

Or:
```
>>> from collections import namedtuple
>>> a = namedtuple("a", "c d")
>>> b = a(2,3)
>>> with MapGetter(b):
...     from b import c, d
>>> print(c, d)
2, 3
```

It works with Python 3.4+ "enum"s - which is great as it allow one
to use the enums by their own name, without having to prepend the Enum class
everytime:
```
>>> from enum import Enum

>>> class Colors(tuple, Enum):
...     red = 255, 0, 0
...     green = 0, 255, 0
...     blue = 0, 0, 255
...

>>> with MapGetter(Colors):
...    from Colors import red, green, blue
...

>>> red
<Colors.red: (255, 0, 0)>
>>> red[0]
255
```

MapGetter can also have a `default` value or callable which
will generate values for each name that one tries to "import" from it:

```
>>> with MapGetter(default=lambda x: x) as x:
...    from x import foo, bar, baz
...

>>> foo
'foo'
>>> bar
'bar'
>>> baz
'baz'
```

If the parameter default is not a callable, it is assigned directly to
the imported names. If it is a callable, MapGetter will try to call it passing
each name as the first and only positional parameter. If that fails
with a type error, it calls it without parameters the way collections.defaultdict
works.


The syntax `from <mydict> import key1 as var1` works as well.

## BijectiveDict
This is a bijective dictionary for which each pair key, value added
is also added as value, key.

The explictly inserted keys can be retrieved as the "assigned_keys"
attribute - and a dictionary copy with all such keys is available
at the "BijectiveDict.assigned".
Conversely, the generated keys are exposed as "BijectiveDict.generated_keys"
and can be seen as a dict at "Bijective.generated"

```
>>> from extradict import BijectiveDict
>>>
>>> a = BijectiveDict(b = 1, c = 2)
>>> a
BijectiveDict({'b': 1, 2: 'c', 'c': 2, 1: 'b'})
>>> a[2]
'c'
>>> a[2] = "d"
>>> a["d"]
2
>>> a["c"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/gwidion/projetos/extradict/extradict/reciprocal_dict.py", line 31, in __getitem__
    return self._data[item]
KeyError: 'c'
>>>
```

## namedtuple
Alternate, clean room, implementation of 'namedtuple' as in stdlib's collection.namedtuple
. This does not make use of "eval" at runtime - and can be up to 10 times faster to create
a namedtuple class than the stdlib version.

Instead, it relies on closures to do its magic.

However, these will be slower to instantiate tahn stdlib version. The "fastnamedtuple"
is faster in all respects, although it holds the same API for instantiating as tuples, and
performs no lenght checking.


## fastnamedtuple
Like namedtuple but the class returned take an iterable for its values
rather than positioned or named parameters. No checks are made towards the iterable
lenght, which should match the number of attributes
It is faster for instantiating as compared with stdlib's namedtuple


## defaultnamedtuple
Implementation of named-tuple using default parameters -
Either pass a sequence of 2-tupes (or an OrderedDict) as the second parameter, or
send in kwargs with the default parameters, after the first.
(This takes advantadge of python3.6 + guaranteed ordering of **kwargs for a function
see https://docs.python.org/3.6/whatsnew/3.6.html)

The resulting object can accept positional or named parameters to be instantiated, as a
normal namedtuple, however, any omitted parameters are used from the original
mapping passed to it.


## FallbackNormalizedDict
Dictionary meant for text only keys:
will normalize keys in a way that capitalization, whitespace and
punctuation will be ignored when retrieving items.

A parallel dictionary is maintained with the original keys,
so that strings that would clash on normalization can still
be used as separated key/value pairs if original punctuation
is passed in the key.

Primary use case if for keeping translation strings when the source
for the original strings is loose in terms of whitespace/punctuation
(for example, in an http snippet)


## NormalizedDict
Dictionary meant for text only keys:
will normalize keys in a way that capitalization, whitespace and
punctuation will be ignored when retrieving items.

Unlike FallbackNormalizedDict this does not keep the original
version of the keys.
