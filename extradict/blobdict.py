from collections import UserDict
from collections.abc import MutableSet
from threading import RLock

import math


class _BlobSliceSet(MutableSet):
    def __init__(self,  parent, offset, length):
        self.parent = parent
        self.offset = offset
        self.length = length
        raw_data = self.parent.data[offset + 1: offset + length + 1].split(b"\x00\x00",1)[0]
        self.data = {word.decode("utf-8") for word in raw_data.split(b"\x00")}


    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def add(self, item):
        raise NotImplementedError()
    def discard(self, item):
        self.data.discard(item)
        self.parent._force_content(self.offset, self.parent._encode(self.data))

    def repr(self):
        return f"{self.__class__.__name__}({{{', '.join(self)}}})"




class _BlobSets:
    def __init__(self, size_hint=1024):
        """
        Binary map per entry: first byte lower 7 bits indicates the log(2, entry_size). (entry is 2** (value & 0x7f) long). high bit indicates whether entry is in use or is deleted.
        """
        self.data = bytearray(b"\x00" * size_hint)
        self.offsets = list()
        self.lock = RLock()

    def _encode(self, data):
        words = []
        for word in data:
            if "\x00" in word:
                raise ValueError(f"{self.__class__.__name__} can't contain words with a \\x00 xharacter")
            words.append(word)
        return b"\x00".join(word.encode("utf-8") for word in words)


    def add_new(self, data):
        with self.lock:
            if not self.offsets:
                offset = 0
            else:
                last_offset = self.offsets[-1]
                offset = last_offset + 2**(self.data[last_offset] & 0x7f)
            self.offsets.append(offset)

            data_bytes = self._encode(data)

            size = len(data_bytes)
            req_size = math.ceil(math.log(size + 3, 2))

            if len(self.data) < offset + 2 ** req_size:
                # ad-hoc heuristics follows: double size until we reach 4MB then go 4MB at a time
                increase = min(2 ** 22, len(self.data))
                self.data.extend(b"\x00" * increase)

            self.data[offset] = 0x80 | req_size
            self._force_content(offset, data_bytes)
        return offset

    def _force_content(self, offset, data_bytes):
        with self.lock:
            self.data[offset + 1: offset + len(data_bytes) + 3] = data_bytes + b"\x00\x00"


    def get(self, offset):
        return _BlobSliceSet(self, offset, 2 ** (self.data[offset] & 0x7f))




class BlobTextDict(UserDict):
    def __setitem__(self, key, value: "Iterable[str]"):
        ...

    def __getitem__(self, key):
        offset = self.data[key]
        return self.blob.get(offset)
