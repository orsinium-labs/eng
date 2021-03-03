from typing import NamedTuple


class Replacement(NamedTuple):
    row: int
    col: int
    word_from: str
    word_to: str
