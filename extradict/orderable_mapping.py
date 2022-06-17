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

from collections.abc import Mapping, MutableMapping
from copy import copy
from threading import RLock

class OrderableMapping(MutableMapping):
    """Mapping allowing custom ordenation of inserted keys.

    By default, insertion order is used. A custom key maybe passed,
    as a callable similar to the one passed to "sorted' builtin.


    """
    def __init__(
            self,
            initial: "Union[Mapping, Sequence[tuple[hashable, any]]|None"=None,
            *,
            key = None,
        ):
        self.data = {}
        self.order = []
        self.lock = RLock()
        self._inserting = False  # state used when inserting a field at a specific position
        if not initial:
            return
        if isinstance (initial, Mapping):
            initial = initial.items()
        for key,value in initial:
            self[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        with self.lock:
            if key not in self.data and not self._inserting:
                self.order.append(key)
            self.data[key] = value

    def __delitem__(self, key):
        with self.lock:
            del self.data[key]
            self.order.remove(key)

    def insert(self, pos, key, value):
        with self.lock:
            self._inserting = True
            self[key] = value
            self.order.insert(pos, key)
            self._inserting = False

    def move(self, key, pos):
        with self.lock:
            self.order.remove(key)
            self.order.insert(pos, key)

    def copy(self):
        return copy(self)

    def __copy__(self):
        instance = self.__class__()
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

