import re
import tokenize
import typing


REX_WORD = re.compile(r'[a-z]{4,}', re.IGNORECASE)


class Replacement(typing.NamedTuple):
    row: int
    col: int
    word_from: str
    word_to: str

    @classmethod
    def from_token(
        cls,
        token: tokenize.TokenInfo,
        words: typing.Mapping[str, str],
    ) -> typing.Iterator['Replacement']:
        for row_offset, line in enumerate(token.string.split('\n')):
            col_offset = 0
            if not row_offset:
                col_offset = token.start[1]
            for match in REX_WORD.finditer(line):
                old_word = match.group(0)
                new_word = words.get(old_word)
                if new_word is None:
                    continue
                if old_word.istitle():
                    new_word = new_word.title()
                yield cls(
                    row=token.start[0] - 1 + row_offset,
                    col=match.start() + col_offset,
                    word_from=old_word,
                    word_to=new_word,
                )
