"""Perform some naive timing experiments
comparing native Python namedtuples and
extradic namedtuple variants
"""


from collections import namedtuple as std_namedtuple
from extradict import namedtuple as extra_namedtuple
from extradict import fastnamedtuple
from extradict import defaultnamedtuple

from timeit import timeit


def main(number=100000):
    variants = [
        (
            "Stdlib collection.namedtuple, create class and instantiate",
            std_namedtuple,
            "a = namedtuple('a', 'a b c d'); a(1, 2, 3, 4)",
            "",
        ),
        (
            "extradict.namedtuple, create class and instantiate",
            extra_namedtuple,
            "a = namedtuple('a', 'a b c d'); a(1, 2, 3, 4)",
            "",
        ),
        (
            "extradict.fastnamedtuple, create class and instantiate",
            fastnamedtuple,
            "a = namedtuple('a', 'a b c d'); a((1, 2, 3, 4))",
            "",
        ),
        (
            "extradict.defaultnamedtuple, create class and instantiate",
            defaultnamedtuple,
            "a = namedtuple('a', {'a':1, 'b':2, 'c':3, 'd':4}); a()",
            "",
        ),
        (
            "Stdlib collection.namedtuple, instantiate",
            std_namedtuple,
            "a(1, 2, 3, 4)",
            "a = namedtuple('a', 'a b c d')",
        ),
        (
            "extradict.namedtuple,  instantiate",
            extra_namedtuple,
            "a(1, 2, 3, 4)",
            "a = namedtuple('a', 'a b c d')",
        ),
        (
            "extradict.fastnamedtuple, instantiate",
            fastnamedtuple,
            "a((1, 2, 3, 4))",
            "a = namedtuple('a', 'a b c d')",
        ),
        (
            "extradict.fastnamedtuple, instantiate",
            defaultnamedtuple,
            "a()",
            "a = namedtuple('a', {'a':1, 'b':2, 'c':3, 'd':4})",
        ),
    ]
    for variant in variants:
        time = timeit(
            variant[2],
            setup=variant[3],
            number=number,
            globals={"namedtuple": variant[1]},
        )
        print(f"{variant[0]} {number} times: {time:.04f}s")


if __name__ == "__main__":
    main()
