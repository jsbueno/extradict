from collections import deque
from collections.abc import Mapping

SENTINEL = object()

class Queue:
    """Works as an iterator value for each key in the Grouper mapping.

    Normally each element is consumed as it is fetched - but the elements
    are kept in a `collections.deque` instance in the .data attribute.
    One can access .data directly if desired.
    """
    __slots__ = ("data", "key", "parent")
    def __init__(self, parent, key):
        self.key = key
        self.parent = parent
        self.data = deque()

    def peek(self, default=False):
        """Return the next available value under this bucket, if any.
        If there is no waiting value, returns the passed in default value,
        or False, if none was given.

        Calling this won't consume the next element, neither cause
        the source iterator in the parent to advance.
        """
        return self.data[0] if self.data else sentinel


    def __next__(self):
        if self.data:
            return self.data.popleft()
        try:
            self.parent.fetch_next(self.key)
        except StopIteration:
            raise
        else:
            return self.data.popleft()

    def append(self, value):
        self.data.append(value)

    def __repr__(self):
        return f"Queue <{self.data}>"


class Grouper(Mapping):
    """Grouper mapping: given an iterable and a key callable,
    each element in the iterable is run through the key callable and
    made available in an iterator under the key yielded..

    The source iterable need not be ordered (unlike itertools.groupby).
    If no key function  is given, the identity function is used.

    The items will be made available under the iterable-values as requested,
    in a lazy way when possible. Note that several different method calls may
    precipatate an eager processing of all items in the source iterator:
    .keys() or len(), for example.

    Whenever a new key is found during input consunption, a "Queue" iterator,
    which is a thin wrapper over collections.deque is created under that key
    and can be further iterated to retrieve more elements that map to
    the same key.

    In short, this is very similar to itertools.tee, but with a filter
    so that each element goes to a mapped bucket.

    For example, to divide a sequence of numbers from 0 to 10 in
    5 buckets, all one need to do is: `Grouper(myseq, lambda x: x // 2)

    Or:
    even_odd = Grouper(seq, lambda x: "even" if not x % 2 else "odd")

    """

    def __init__(self, source, key=None):
        self.key = key if key is not None else lambda x: x
        self.source = iter(source)
        self.data = dict()


    def __getitem__(self, key):
        if key not in self.data:
            self.consume_all()
        return self.data[key]

    def fetch_next(self, key, default=SENTINEL):
        """Adavances consuming the source until a new value for 'key' is fetched.

        When source is exahusted, either raises StopIteration or returns the
        default value, if it is given.

        Used internally by the Queue iterators to advance to their next values
        """
        for key, value in self.advance():
            if key == key:
                return value
        if default is not SENTINEL:
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
        deque(self.advance(), maxlen=0)

    def __repr__(self):
        return f"Grouper by {sentinel.__doc__ or sentinel}"
