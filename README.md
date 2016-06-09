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
A Context manager that allows one to pick variables from inside a dictionary
(or mapping) by using the  `from <mydict> import key1, key2` statement.



```
>>> from extradict import MapGetter
>>> a = dict(b="test", c="another test")
>>> with MapGetter(a) as a:
...     from a import b, c
...
>>> print (b, c)
test another test
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