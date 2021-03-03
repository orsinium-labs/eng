import tokenize
import re
import typing
from ._replacement import Replacement

HandlerType = typing.Callable[
    [tokenize.TokenInfo, typing.Mapping[str, str]],
    typing.Iterator[Replacement],
]
REX_WORD = re.compile(r'[a-z]{4,}', re.IGNORECASE)

HANDLERS: typing.Dict[int, HandlerType]
HANDLERS = {}


def register(node: int):
    def wrapper(handler: HandlerType):
        HANDLERS[node] = handler
        return handler
    return wrapper


@register(tokenize.STRING)
def handle_str(
    token: tokenize.TokenInfo,
    words: typing.Mapping[str, str],
) -> typing.Iterator[Replacement]:
    for match in REX_WORD.finditer(token.string):
        old_word = match.group(0)
        new_word = words.get(old_word)
        if new_word is None:
            continue
        if old_word.istitle():
            new_word = new_word.title()
        yield Replacement(
            row=token.start[0] - 1,
            col=token.start[1] + match.start(),
            word_from=old_word,
            word_to=new_word,
        )
