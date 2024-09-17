from __future__ import annotations

from collections import deque
from collections.abc import Mapping
import typing as T


SENTINEL = object()


class Queue:
    """Used as bucket class by Grouper. Works as an iterator value for each key in the Grouper mapping.

    Normally each element is consumed as it is fetched - but the elements
    are kept in a `collections.deque` instance in the .data attribute.
    One can access .data directly if desired.
    """

    __slots__ = ("data", "key", "parent")

    def __init__(self, parent: Grouper, key: T.Hashable):
        self.key = key
        self.parent = parent
        self.data = deque()

    def peek(self, default: T.Any = False) -> T.Any:
        """Return the next available value under this bucket, if any.
        If there is no waiting value, returns the passed in default value,
        or False, if none was given.

        Calling this won't consume the next element, neither cause
        the source iterator in the parent to advance.
        """
        return self.data[0] if self.data else default

    def __iter__(self):
        return self

    def __next__(self):
        if self.data:
            return self.data.popleft()
        try:
            self.parent.fetch_next(self.key)
        except StopIteration:
            raise
        else:
            return self.data.popleft()

    def append(self, value: T.Any) -> None:
        """Used internally by the parnt grouper to feed the filtered data"""
        self.data.append(value)

    def __repr__(self):
        return f"Queue <{self.data}>"


class Grouper(Mapping):
    """Grouper mapping:

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
    even_odd = `Grouper(seq, lambda x: "even" if not x % 2 else "odd")`

    """

    def __init__(
        self,
        source: T.Union[T.Sequence, T.Iterable],
        key: T.Callable[[T.Any], T.Hashable] = None,
    ):
        self.key = key if key is not None else lambda x: x
        self.source = iter(source)
        self.data = dict()

    def __getitem__(self, key: T.Hashable):
        if key not in self.data:
            SENTINEL2 = object()
            if self.fetch_next(key, SENTINEL2) is SENTINEL2:
                raise KeyError(key)
        return self.data[key]

    def fetch_next(self, key: T.Hashable, default: T.Any = SENTINEL):
        """Advances consuming the source until a new value for 'key' is fetched.

        When source is exhausted, either raises StopIteration or returns the
        default value, if it is given.

        Used internally by the Queue iterators to advance to their next values
        """
        for new_key, value in self.advance():
            if key == new_key:
                return value
        if default is SENTINEL:
            raise StopIteration
        return default

    def advance(self):
        """A generator that consumes one item from source, feeds the internal buckets
        and yields the (key, value) pair each time it is 'nexted'.

        This is used internally as the mechanism to fill the bucket queues.
        If there the intent is just to consume the source and get the key, value pair
        without storing the values in the buckets, use ".consume()"
        """

        for key, value in self.consume():
            if key not in self.data:
                self.data[key] = Queue(self, key)
            self.data[key].append(value)
            yield key, value

    def consume(self):
        """A generator that consumes one item from source, feeds the internal buckets
        and yields the (key, value) pair each time it is 'nexted'.

        This is used internally as the mechanism to advance the source generator
        and get the corresponding key. The values are not stored for further use,
        and just yielded as key, value pair.

        This can be used directly, but one might just use
        `map(lambda v: (key(v), v), source)` instead of using a Grouper object.

        If this is called directly when trying to make use of the buckets undefined
        results will ensue.
        """
        for value in self.source:
            key = self.key(value)
            yield key, value

    def __iter__(self):
        self.consume_all()
        return iter(self.data)

    def __len__(self):
        self.consume_all()
        return len(self.data.keys())

    def consume_all(self):
        # Consumes all the remaining source
        # this "hidden" recipe is the most efficient
        # way in the cPython interpreter to consume a generator
        # - check: https://docs.python.org/3/library/itertools.html#itertools-recipes
        deque(self.advance(), maxlen=0)

    def __call__(self, keyhint: T.Container[str] = ()) -> dict[T.Hashable, list[T.any]]:
        """Consumes all the source iterator, and returns a plain dictionay with
        all elements inside lists under the appropriate keys. If keyhint
        is passed, keys for which there are no elements are created with
        empty lists. (But extra keys yielded by the key function and
        not present in keyhint will be present in the result, nonetheless).

        The iterators in the Grouper object itself are not themselves consumed
        (although the expected pattern if one calls this is that the resulting
        dictionary is used and the grouper object is discarded)

        """
        keyhint = set(keyhint)
        result = {key: list(self[key].data) for key in self}
        for remaining in keyhint - result.keys():
            result[remaining] = []
        return result

    def __repr__(self):
        return f"Grouper by {self.key}"
