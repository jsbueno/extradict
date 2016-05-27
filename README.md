==================================================
Extra Dictionary classes and utilities for Python
==================================================

New utilities to be added as they are devised


VersionDict
============
A Python Mutable Mapping Container (dictionary :-) ) that
can "remember" previous values.
Use it wherever you would use a dict - at each
key change or update, it's `version` attribute
is increased by one.

The `get` method is modified to receive an optional
named  `version` parameter that allows one to retrieve
for a key the value it contained at that respective version.

NB. When using the `version` parameter, `get` will raise
a KeyError if the key does not exist for that version and
no default value is specified.


Implementation:
_________________
It works by internally keeping a list of (named)tuples with
(version, value) for each key.


Example:
_________

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

OrderedVersionDict
====================
Like VersionDict, but preserves and retrieves key
insertion order. Unlike a plain "collections.OrderedDict",
however, whenever a key's value is updated, it is moved
last on the dictionary order.

Example:
_________

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