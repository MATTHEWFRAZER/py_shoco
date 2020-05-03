from py_shoco.encoding import Encoding

__all__ = ["PACK_STRUCTURES", "ENCODINGS", "MAX_CONSECUTIVES", "MAX_LEADING_CHARACTER_BITS"]

PACK_STRUCTURES = (
    (1, (
        (2, 4, 2),
        (2, 3, 3),
        (2, 4, 1, 1),
        (2, 3, 2, 1),
        (2, 2, 2, 2),
        (2, 3, 1, 1, 1),
        (2, 2, 2, 1, 1),
        (2, 2, 1, 1, 1, 1),
        (2, 1, 1, 1, 1, 1, 1),
    )),
    (2, (
        (3, 5, 4, 2, 2),
        (3, 5, 3, 3, 2),
        (3, 4, 4, 3, 2),
        (3, 4, 3, 3, 3),
        (3, 5, 3, 2, 2, 1),
        (3, 5, 2, 2, 2, 2),
        (3, 4, 4, 2, 2, 1),
        (3, 4, 3, 2, 2, 2),
        (3, 4, 3, 3, 2, 1),
        (3, 4, 2, 2, 2, 2),
        (3, 3, 3, 3, 2, 2),
        (3, 4, 3, 2, 2, 1, 1),
        (3, 4, 2, 2, 2, 2, 1),
        (3, 3, 3, 2, 2, 2, 1),
        (3, 3, 2, 2, 2, 2, 2),
        (3, 2, 2, 2, 2, 2, 2),
        (3, 3, 3, 2, 2, 1, 1, 1),
        (3, 3, 2, 2, 2, 2, 1, 1),
        (3, 2, 2, 2, 2, 2, 2, 1),
    )),
    (4, (
        (4, 5, 4, 4, 4, 3, 3, 3, 2),
        (4, 5, 5, 4, 4, 3, 3, 2, 2),
        (4, 4, 4, 4, 4, 4, 3, 3, 2),
        (4, 4, 4, 4, 4, 3, 3, 3, 3),
    ))

)

ENCODINGS = [(packed, [Encoding(bitlist) for bitlist in bitlists]) for packed, bitlists in PACK_STRUCTURES]

MAX_CONSECUTIVES = 8

MAX_LEADING_CHARACTER_BITS = 5
MAX_SUCCESSOR_BITS = 4
ENCODING_TYPES = 3
