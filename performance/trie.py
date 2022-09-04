"""
Checks the data structure size for the tries
"""

import os
import sys
import time

from extradict.trie import PatternCharTrie, PrefixCharTrie
from pathlib import Path
from datetime import datetime


#######################################################################
##### Taken from https://github.com/bosswissam/pysize
# via
# https://gist.github.com/durden/0b93cfe4027761e17e69c48f9d5c4118

def get_size(obj, seen=None):
    """Recursively finds size of objects"""

    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])

    return size

def timeit(callable_, args=None, kwargs=None):
    start = time.time()
    result = callable_(*(args or ()), **(kwargs or {}))
    end = time.time()
    return end - start, result

def main():
    path = Path("lista_palavras.txt")
    ellapsed_pat, pat = timeit(PatternCharTrie, (data:=[p.strip() for p in path.open()],))
    ellapsed_pref, pref = timeit(PrefixCharTrie, (data,))
    commit = os.popen("git log").read(300).split()[1][:7]
    time = datetime.now().isoformat().split(".")[0]
    log = Path("structure_sizes.txt")
    with log.open("a") as output:
        output.write(", ".join((time, commit, f"{get_size(pat):_}B", f"{ellapsed_pat:.03f}s", f"{get_size(pref):_}B", f"{ellapsed_pref:.03f}s")) + "\n")

if __name__ == "__main__":
    try:
        print("Creating tries with 'lista_de_palavras.txt' and measuring structure size. This might take a few secs.")
        main()
        print("All done - results appended to 'structure_sizes.txt' ")
    except OSError:
        print("Something went wrong - ensure you run this from the project root", file=sys.stderr)




