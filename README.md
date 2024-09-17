# Extra Dictionary classes and utilities for Python

Some Mapping containers and tools for daily use with Python.
This attempts to be a small package with no dependencies,
just delivering its data-types as described bellow
enough tested for production-usage.

 ## What is new in v. 0.7

  - The Trie, PrefixTrie and NormalizedTrie classes! See bottom of file!


## ExtraDict data structures:
  Bellow, a list, in order of implementation, of the public classes
  implemented in this package:

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

`.copy(version=None)`:  yields a copy of the current dictionary at that version, with history preserved
(if version is not given, the current version is used)

`.freeze(version=None)` yields a snapshot of the versionDict in the form of a plain dictionary for
the specified version


### Implementation:
It works by internally keeping a list of (named)tuples with
(version, value) for each key.


### Example:

```python

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
insertion order. Unlike a plain dictionary or `collections.OrderedDict`,
however, whenever a key's value is updated, it is moved
last on the dictionary order.

### Example:
```python
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



```python
>>> from extradict import MapGetter
>>> a = dict(b="test", c="another test")
>>> with MapGetter(a) as a:
...     from a import b, c
...
>>> print (b, c)
test another test
```

Or:
```python
>>> from collections import namedtuple
>>> a = namedtuple("a", "c d")
>>> b = a(2,3)
>>> with MapGetter(b):
...     from b import c, d
>>> print(c, d)
2, 3
```

It works with Python "Enum"s - which is great as it allow one
to use the enums by their own name, without having to prepend the Enum class
every time:
```python
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

```python
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

The explicitly inserted keys can be retrieved as the "assigned_keys"
attribute - and a dictionary copy with all such keys is available
at the "BijectiveDict.assigned".
Conversely, the generated keys are exposed as "BijectiveDict.generated_keys"
and can be seen as a dict at "Bijective.generated"

```python
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

However, these will be slower to instantiate than stdlib version. The "fastnamedtuple"
is faster in all respects, although it holds the same API for instantiating as tuples, and
performs no length checking.


## fastnamedtuple
Like namedtuple but the class returned take an iterable for its values
rather than positioned or named parameters. No checks are made towards the iterable
length, which should match the number of attributes
It is faster for instantiating as compared with stdlib's namedtuple


## defaultnamedtuple
Implementation of named-tuple using default parameters -
Either pass a sequence of 2-tuples or any ordered Mapping (like a `dict`) as the second parameter, or
send in kwargs with the default parameters, after the first.

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
(for example, in an html snippet)


## NormalizedDict
Dictionary meant for text only keys:
will normalize keys in a way that capitalization, whitespace and
punctuation will be ignored when retrieving items.

Unlike FallbackNormalizedDict this does not keep the original
version of the keys.


## TreeDict
A Python mapping with an underlying auto-balancing binary tree data structure.
As such, it allows seeking ranges of keys - so, that
`mytreedict["aa":"bz"] will return a list with all values in
the dictionary whose keys are strings starting from "aa"
up to those starting with "by".

It also features a `.get_closest_keys` method that will
retrieve the closest existing keys for the required element.
```python
>>> from extradict import TreeDict
>>> a = TreeDict()
>>> a[1] = "one word"
>>> a[3] = "another word"
>>> a[:]
['one word', 'another word']
>>> a.get_closest_keys(2)
(1, 3)
```

Another feature of these dicts is that as they
do not rely on an object hash, any Python
object can be used as a key. Of course
key objects should be comparable with <=, ==, >=. If
they are not, errors will be raised. HOWEVER, there is
an extra feature - when creating the TreeDict a named
argument `key` parameter can be passed that works the
same as Python's `sorted` "key" parameter: a callable
that will receive the key/value pair as its sole argument
and should return a comparable object. The returned object
is the one used to keep the Binary Tree organized.


If the output of the given `key_func` ties, that is it:
the new pair simply overwrites whatever other key/value
had the same key_func output. To avoid that,
craft the key_funcs so that they return a tuple
with the original key as the second item:
```python
>>> from extradict import TreeDict
>>> b = TreeDict(key=len)
>>> b["red"] = 1
>>> b["blue"] = 2
>>> b
TreeDict('red'=1, 'blue'=2, key_func= <built-in function len>)

>>> b["1234"] = 5
>>> b
TreeDict('red'=1, '1234'=5, key_func= <built-in function len>)

>>> TreeDict(key=lambda k: (len(k), k))
>>> b["red"] = 1
>>> b["blue"] = 2
>>> b["1234"] = 5
>>> b
>>> TreeDict('red'=1, '1234'=5, 'blue'=2, key_func= <function <lambda> at 0x7fbc7f462320>)
```

### PlainNode and AVLNode

To support the TreeDict mapping interface, the standalone
`PlainNode` and `AVLNode` classes are available at
the `extradict.binary_tree_dict` module - and can be used
to create a lower level tree data structure, which can
have more capabilities. For one, the "raw" use allows
repeated values in the Nodes, all Nodes are root to
their own subtrees and know nothing of their parents,
and if one wishes, no need to work with "key: value" pairs:
if a "pair" argument is not supplied to a Node, it
reflects the given Key as its own value.

`PlainNode` will build non-autobalancing trees,
while those built with `AVLNode` will be self-balancing.
Trying to manually mix node types in the same tree, or
changing the key_func in different notes,
will obviously wreck everything.

## Grouper


Think of it as an itertools.groupby which returns a mapping
Or as an itertools.tee that splits the stream into filtered
substreams according to the passed key-callable.

Given an iterable and a key callable,
each element in the iterable is run through the key callable and
made available in an iterator under a bucket using the resulting key-value.

The source iterable need not be ordered (unlike itertools.groupby).
If no key function  is given, the identity function is used.

The items will be made available under the iterable-values as requested,
in a lazy way when possible. Note that several different method calls may
precipatate an eager processing of all items in the source iterator:
.keys() or len(), for example.

Whenever a new key is found during input consumption, a "Queue" iterator,
which is a thin wrapper over collections.deque is created under that key
and can be further iterated to retrieve more elements that map to
the same key.

In short, this is very similar to `itertools.tee`, but with a filter
so that each element goes to a mapped bucket.

Once created, the resulting object may obtionally be called. Doing this
will consume all data in the source iterator at once, and return a
a plain dictionary with all data fetched into lists.

For example, to divide a sequence of numbers from 0 to 10 in
5 buckets, all one need to do is: `Grouper(myseq, lambda x: x // 2)`

Or:
```python
>>> from extradict import Grouper
>>> even_odd = Grouper(range(10), lambda x: "even" if not x % 2 else "odd")
>>> print(list(even_odd["even"]))
[0, 2, 4, 6, 8]
>>> print(list(even_odd["odd"]))
[1, 3, 5, 7, 9]

```


## NestedData

Nestable mappings and sequences data structure to facilitate field access

The idea is a single data structure that can hold "JSON" data, adding some
helper methods and functionalities.

Primarily, one can use a dotted string path to access a deply nested key, value pair,
instead of concatenating several dictionary ".get" calls.

Examples:
      `person["address.city"] instead of person["address"]["city"]`

      or

      `persons["10.contacts.emails.0"]`


The first tool available is the ability to merge mappings with extra keys
into existing nested mappings, without deleting non colidng keys:
a "person.address" key that would contain "city" but no "street" or "zip-code"
can be updated with:  `record["person"].merge({"address": {"street": "5th ave", "zip-code": "000000"}})`
preserving the "person.address.city" value in the process.

The ".data" attribute stores the object contents as a tree of dicionary and lists as needed -
these are lazily wrapped as NestedData instances if retrieved through the class, but
can be freely manipulated directly.

```python
>>> import json
>>> from extradict import NestedData
>>> a = NestedData(json.load(open("myfile.json")))
>>> assert a["persons.0.address"] == a["persons"][0]["address"]
True
>>> a.merge({"city": None}, "persons.*.address")  # creates a new "city" key in all addresses
```

## PrefixTrie
A Trie data structure with a `set`-like interface. It should contain
strings - and after picking a prefix by using the square bracket notation
for mappings, it returns a view of the data which only contains the matching
elements. (data is not dduplicated unferlying).

Unlike, for example, running a regexp against a list
with several thousand words, which will have to walk through
all entries, these Tries really only descend into the entries
which match the given pattern, never touching any unmacthed
entry.

Can be used IRL for auto-completing text:

```python
>>> from extradict import PrefixTrie
>>> a = PrefixTrie(["abc", "abcd", "def", "defg"])
>>> len(a)
4
>>> list(a["ab"])
['abcd', 'abc']
>>> list(a["def"])
['defg', 'def']
```
## Trie
An evolution of PrefixTrie, which will match any pattern
in the middle of the member strings, not only as a prefix:

```python
>>> from extradict import Trie
>>> a = Trie(["abc", "zabc", "def", "bcdef"])
>>> list(a["bc"])
['zabc', 'abc', 'bcdef']
```

## NormalizedTrie
A Trie that will match patterns in the middle,
but internally keeps a helper `NormalizedDict`
structure which will make it ignore differences
due to punctiation, space and accented characters -
making it ideal for real world text-completion finding.


```python
>>> from extradict import NormalizedTrie
>>>
>>> a = NormalizedTrie(("a-b-c", "abc", "maca", "maçã"))
>>> list(a["bc"])
['abc', 'a-b-c']
>>> list(a["mac"])
['maca', 'maçã']
>>> list(a["macã"])
['maca', 'maçã']
```

```

