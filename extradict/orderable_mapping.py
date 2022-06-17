# Copyright 2022 João S. O. Bueno <https://github.com/jsbueno/>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.

#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# First version of this worked as part of turicas/rows project.

# (type annotations temporarily provided for doc. puroposes only)

from collections.abc import Mapping, MutableMapping, MutableSequence
from copy import copy
from threading import RLock

class _LLNode:
    __slots__ = "value next prev".split()
    def __init__(self, value, next=None, prev=None):
        self.value = value
        self.next = next
        self.prev = prev

    def __repr__(self):
        return f"_N<{'^' if self.prev is None else '...'}, {self.value!r}, {'$' if self.next is None else '...'}>"


class _LL(MutableSequence):
    # Naive linked list to go along OrderableMapping
    def __init__(self, initial=None):
        self.head = None
        self.tail = None
        self.lock = RLock()
        self._length = 0
        if initial:
            for item in initial:
                self.append(item)

            #initial = iter(initial)
            #self.head = _LLNode(next(initial, None))
            #prev = self.head
            #for value in initial:
                #prev.next = current = _LLNode(value)
                #current.prev = prev
        #self.tail = current

    def __getitem__(self, index):
        return self._getnode(index).value

    def _getnode(self, index):
        if not self.head:
            raise IndexError()
        current = self.head if index >= 0 else self.tail
        for i in range(0, index, 1 if index > 0 else -1):
            with self.lock:
                if index > 0:
                    with self.lock:
                        current = current.next
                else:
                    current = current.prev
            if current is None:
                raise IndexError()
        return current

    def __setitem__(self, index, value):
        if index >= len(self):
            raise IndexError()
        node_at_index = _getnode(index)
        node_at_index.value = value
        prev = node_at_index.prev

    def _insert_before_node(self, node, value):
        if not isinstance(value, _LLNode):
            value = _LLNode(value)
        else:
            value.next = value.prev = None
        with self.lock:
            if node.prev:
                value.prev = node.prev
                node.prev.next = value
            else:
                if node is not self.head:
                    raise ValueError("Reference node for insertion not part of this linkedlist")
                self.head = value
            value.next = node
            node.prev = value

    def insert(self, index, value):
        node = _LLNode(value)
        if index >= len(self):
            self.append(value)
            return
        node_at_index = self._getnode(index)
        prev = node_at_index.prev
        with self.lock:
            if prev:
                prev.next = node
            else:
                self.head = node
            node.next = node_at_index
            node_at_index.prev = node
            self._length += 1

    def append(self, value):
        node = _LLNode(value)
        with self.lock:
            if self.tail is None:
                self.head = self.tail = node
            else:
                node.prev = self.tail
                node.prev.next = node
                self.tail = node
            self._length += 1

    def _iter_nodes(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def __iter__(self):
        for node in self._iter_nodes():
            yield node.value

    def __delitem__(self, index):
        node_at_index = self._getnode(index)
        with self.lock:
            if node_at_index.prev:
                node_at_index.prev.next = node_at_index.next
            if node_at_index.next:
                node_at_index.next.prev = node_at_index.prev
            self._length -= 1

    def __len__(self):
        return self._length

    def __copy__(self):
        # Nodes have to be recreated on a shallow copy:
        return self.__class__(iter(self))

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self)})"


class OrderableMapping(MutableMapping):
    """Mapping allowing custom ordenation of inserted keys.

    By default, insertion order is used. A custom key maybe passed,
    as a callable similar to the one passed to "sorted' builtin, but which takes
    the key and value of each dictionary item as positional parameters.

    Example: instance that will keep the keys ordered by the value order:
    mymap = OrderableMapping(key=lambda k, v: v)

    Insertions and retrieval by position (.get_at) are O(N) for custom keys, O(1) for
    insertion-order key. (Iterating keys in sorted order is linear in both cases)

    """
    def __init__(
            self,
            initial: "Union[Mapping, Sequence[tuple[hashable, any]]|None"=None,
            *,
            key = None,
        ):
        self.data = {}
        self.order = [] if key is None else _LL()
        self.lock = RLock()
        self._key = key
        self._inserting = False  # state used when inserting a field at a specific position
        if not initial:
            return
        if isinstance (initial, Mapping):
            initial = initial.items()
        for key,value in initial:
            self[key] = value

    key = property(lambda self: self._key)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        with self.lock:
            if self.key:
                insertion_key = self.key(key, value)
                if key in self.data:
                    old_value = self.data[key]
                    old_insertion_key = self.key(key, old_value)
                    if old_insertion_key == insertion_key:  # Key function does not rely on value, or order would not be changed anyway
                        self.data[key] = value
                    else:
                        del self[key]

                if key not in self.data:  # Not an ΅else" as the old key might have been just deleted
                    for index, order_node in enumerate(self.order._iter_nodes()):
                        order_key = order_node.value
                        order_value = self.data[order_key]
                        if insertion_key < self.key(order_key, order_value):
                            self.order._insert_before_node(order_node, key)
                            break
                    else:
                        self.order.append(key)
            else:  # default no key (order-of-insertion) path:
                if key not in self.data and not self._inserting:
                        self.order.append(key)
            self.data[key] = value

    def __delitem__(self, key):
        with self.lock:
            del self.data[key]
            self.order.remove(key)

    def get_at(self, index):
        """retrieve the item (key, value) at index position. i.e.: use the ordering instead of the key"""
        key = self.order[index]
        return key, self.data[key]

    def insert(self, pos, key, value):
        if self.key:
            raise TypeError("Can't insert item at arbitrary position for custom-keyed mappings")
        with self.lock:
            self._inserting = True
            self[key] = value
            self.order.insert(pos, key)
            self._inserting = False

    def move(self, key, pos):
        if self.key:
            raise TypeError("Can't move item for custom-keyed mappings")
        with self.lock:
            self.order.remove(key)
            self.order.insert(pos, key)

    def copy(self):
        return copy(self)

    def __copy__(self):
        instance = self.__class__(key=self.key)
        with instance.lock, self.lock:
            instance.data = copy(self.data)
            instance.order = copy(self.order)
        return instance

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from iter(self.order)

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self.items())})"

