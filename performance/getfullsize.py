"""code by Joao S. O. Bueno

first posted at https://stackoverflow.com/questions/77908879/why-python-allocate-memory-to-string-is-different-strategy/77908901#77908901

Can be used undere
Stackoverflow license terms or LGPL 3.0+
"""

from sys import getsizeof

def getfullsize(obj, seen=None):
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = getsizeof(obj)
    if not isinstance (obj, (str, bytes)) and hasattr(type(obj), "__len__"):
        for item in obj:
            if hasattr(type(obj), "values"):
                size += getfullsize(obj[item], seen)

            size += getfullsize(item, seen)
    if hasattr(obj, "__dict__"):
        size += getfullsize(obj.__dict__, seen)
    if hasattr(obj, "__slots__"):
        for attr in obj.__slots__:
            if (item:=getattr(obj, attr, None)) is not None:
                size+= getfullsize(item, seen)
    return size
