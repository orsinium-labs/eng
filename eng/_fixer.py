import ast
import enum
import typing
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from ._replacement import Replacement
from ._handlers import HANDLERS


class Target(enum.Enum):
    US = 'us'
    UK = 'uk'


@lru_cache(maxsize=2)
def get_words(target: Target) -> typing.Mapping[str, str]:
    path = Path(__file__).parent / 'words.txt'
    result = {}
    for line in path.open('r', encoding='utf8'):
        line = line.strip()
        if not line:
            continue
        uk, us = line.split('\t')
        if target == Target.US:
            result[uk] = us
        else:
            result[us] = uk
    return MappingProxyType(result)


class Fixer:
    target: Target
    tree: ast.Module
    content: str

    def __init__(self, *, target: Target = Target.US, content: str) -> None:
        self.target = target
        self.content = content
        self.tree = ast.parse(content)

    @classmethod
    def from_path(cls, path: Path, **kwargs) -> 'Fixer':
        content = path.read_text(encoding='utf8')
        return cls(content=content, **kwargs)

    @property
    def words(self) -> typing.Mapping[str, str]:
        return get_words(target=self.target)

    @property
    def replacements(self) -> typing.Iterator[Replacement]:
        for node in ast.walk(self.tree):
            handler = HANDLERS.get(type(node))
            if handler is None:
                continue
            yield from handler(node, self.words)

    def apply(self) -> str:
        reps = sorted(self.replacements, reverse=True)
        lines = self.content.split('\n')
        for rep in reps:
            line = lines[rep.row]
            line_before = line[:rep.col]
            line_after = line[rep.col + len(rep.word_from):]
            line = line_before + rep.word_to + line_after
            lines[rep.row] = line
        return '\n'.join(lines)
