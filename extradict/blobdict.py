from collections import UserDict
from collections.abc import MutableSet, Iterable
from threading import RLock

import math

_OVERHEAD = 3
_SIZE_MASK = 0x7F
_IN_USE_MASK = 0x80


class _BlobSliceSet(MutableSet):
    def __init__(self, parent, offset, length):
        self.parent = parent
        self.offset = offset
        self.length = length
        raw_data = self.parent.data[offset + 1 : offset + length + 1].split(
            b"\x00\x00", 1
        )[0]
        self.data = {word.decode("utf-8") for word in raw_data.split(b"\x00")}

    def __contains__(self, item):
        return item in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def add(self, item):
        self.data.add(item)
        self.offset = self.parent._store(self.offset, self.data)

    def discard(self, item):
        self.data.discard(item)
        self.parent._force_content(self.offset, self.parent._encode(self.data))

    def __repr__(self):
        return f"{self.__class__.__name__}({{{', '.join(self)}}})"


class _BlobSets:
    def __init__(self, size_hint=1024):
        """
        Binary map per entry: first byte lower 7 bits indicates the log(2, entry_size). (entry is 2** (value & 0x7f) long). high bit indicates whether entry is in use or is deleted.
        """
        self.data = bytearray(b"\x00" * size_hint)
        self.offsets = list()  # maybe just track "last_offset"?
        self.lock = RLock()

    def _encode(self, data):
        words = set()
        for word in data:
            if "\x00" in word:
                raise ValueError(
                    f"{self.__class__.__name__} can't contain words with a \\x00 xharacter"
                )
            words.add(word)
        return b"\x00".join(word.encode("utf-8") for word in words)

    def add_new(self, data: "Iterable[str]"):
        """Adds a new string-set in a newly allocated point in the blob. Returns data offset to be used in .get"""
        if isinstance(data, str):
            raise TypeError("data must be a  non-string iterable of strings")
        with self.lock:

            self.offsets.append(offset := self._get_next_offset())

            data_bytes = self._encode(data)

            size = len(data_bytes)
            log_req_size = self._get_log_size(size)

            self._ensure_size(offset + 2**log_req_size)

            self.data[offset] = _IN_USE_MASK | log_req_size
            self._force_content(offset, data_bytes)
        return offset

    def _store(self, offset, data):
        data_bytes = self._encode(data)
        size = len(data_bytes)
        capacity = 2 ** (self.data[offset] & _SIZE_MASK)
        if size + _OVERHEAD <= capacity:
            self._force_content(offset, data_bytes)
            return offset
        new_offset = self._realloc(offset, len(data_bytes) + _OVERHEAD)
        self._force_content(new_offset, data_bytes)
        return new_offset

    def _get_next_offset(self):
        if not self.offsets:
            offset = 0
        else:
            last_offset = self.offsets[-1]
            offset = last_offset + 2 ** (self.data[last_offset] & _SIZE_MASK)
        return offset

    def _get_log_size(self, byte_size):
        # The "_OVERHEAD" is to ensure space for 1 header byte + 2 byte termination sequence (b"\x00\x00")
        return math.ceil(
            max(math.log(byte_size + _OVERHEAD, 2), 3)
        )  # minimal 8 bytes: allow posting a forwarding offset

    def _ensure_size(self, req_size):
        with self.lock:
            if len(self.data) < req_size:
                # ad-hoc heuristics follows: double size until we reach 4MB then go 4MB at a time
                increase = min(2**22, len(self.data))
                self.data.extend(b"\x00" * increase)

    def _realloc(self, old_offset, new_size):
        with self.lock:
            self._ensure_size(new_size + self.offsets[-1] if self.offsets else 0)
            content = self.data[
                old_offset + 1 : old_offset + 2 ** (self.data[old_offset] & _SIZE_MASK)
            ]
            self.data[old_offset] &= _SIZE_MASK
            self.offsets.append(new_offset := self._get_next_offset())
            self.data[new_offset] = _IN_USE_MASK | self._get_log_size(new_size)
            self.data[new_offset + 1 : len(content)] = content
            self.data[old_offset + 1 : old_offset + 7] = new_offset.to_bytes(
                6, "little"
            )
        return new_offset

    def _final_offset(self, offset):
        "Tracks the final destination of existing data"
        while not (self.data[offset] & _IN_USE_MASK):
            offset = int.from_bytes(self.data[offset + 1 : offset + 7], "little")
        return offset

    def _force_content(self, offset, data_bytes):
        with self.lock:
            self.data[offset + 1 : offset + len(data_bytes) + _OVERHEAD] = (
                data_bytes + b"\x00\x00"
            )

    def get(self, offset):
        """Retrieves the data contents at the given offset as a set-like object

        Automatically picks the new offset if the orignal data has been realocated
        at some point.

        (as of Python 3.12 an ampty set is 216 bytes long on x86_64 -
        we are down to 16 or 20 bytes per entry with up to 3 single characters here)
        """
        offset = self._final_offset(offset)
        return _BlobSliceSet(self, offset, 2 ** (self.data[offset] & _SIZE_MASK))


class BlobTextDict(UserDict):
    """Mapping wrapper over _BlobSets

    A dictionary with arbitrary keys and sets of string as values
    which will hold data in a single binary blob, instead of one
    Python set instance for each entry.
    """

    def __init__(self, *args, **kwargs):
        self.blob = _BlobSets()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value: "Iterable[str]"):
        value_offset = self.blob.add_new(value)
        super().__setitem__(key, value_offset)

    def __getitem__(self, key):
        try:
            offset = super().__getitem__(key)
        except KeyError:
            super().__setitem__(key, offset := self.blob.add_new(set()))

        return self.blob.get(offset)

    def __repr__(self):
        return f"{self.__class__.__name__}({{{', '.join(key + ':' + repr(value) for key, value in self.items())}}})"
