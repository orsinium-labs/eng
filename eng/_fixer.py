import enum
import re
import tokenize
import typing
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType

from ._replacement import Replacement


REX_STRING = re.compile(r'\"[^"\\]*(?:\\.[^"\\]*)*"')


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
    content: str

    def __init__(self, *, target: Target = Target.US, content: str) -> None:
        self.target = target
        self.content = content

    @property
    def words(self) -> typing.Mapping[str, str]:
        return get_words(target=self.target)

    @property
    def replacements(self) -> typing.Iterator[Replacement]:
        raise NotImplementedError

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


class PythonFixer(Fixer):
    @property
    def tokens(self) -> typing.Tuple[tokenize.TokenInfo, ...]:
        lines = self.content.split('\n')
        callback = (line + '\n' for line in lines).__next__
        return tuple(tokenize.generate_tokens(callback))

    @property
    def replacements(self) -> typing.Iterator[Replacement]:
        for token in self.tokens:
            if token.type not in {tokenize.STRING, tokenize.COMMENT}:
                continue
            yield from Replacement.from_token(token, self.words)


class TextFixer(Fixer):
    @property
    def replacements(self) -> typing.Iterator[Replacement]:
        token = tokenize.TokenInfo(
            type=tokenize.STRING,
            string=self.content,
            start=(1, 0),
            end=(2, 0),
            line=self.content,
        )
        yield from Replacement.from_token(token, self.words)


class LiteralFixer(Fixer):
    @property
    def replacements(self) -> typing.Iterator[Replacement]:
        for row_offset, line in enumerate(self.content.split('\n')):
            for match in REX_STRING.finditer(line):
                token = tokenize.TokenInfo(
                    type=tokenize.STRING,
                    string=match.group(0),
                    start=(1+row_offset, match.start()),
                    end=(2+row_offset, 0),
                    line=self.content,
                )
                yield from Replacement.from_token(token, self.words)
