import ast
import re
import typing
from ._replacement import Replacement

HandlerType = typing.Callable[[ast.AST, typing.Mapping[str, str]], typing.Iterator[Replacement]]
REX_WORD = re.compile(r'[a-z]{4,}', re.IGNORECASE)

HANDLERS: typing.Dict[typing.Type[ast.AST], HandlerType]
HANDLERS = {}


def register(node: typing.Type[ast.AST]):
    def wrapper(handler: HandlerType):
        HANDLERS[node] = handler
        return handler
    return wrapper


@register(ast.Str)
def handle_str(
    node: ast.Str, words: typing.Mapping[str, str],
) -> typing.Iterator[Replacement]:
    return _handle_text(text=node.s, node=node, words=words, offset_col=1)


@register(ast.Constant)
def handle_const(
    node: ast.Constant, words: typing.Mapping[str, str],
) -> typing.Iterator[Replacement]:
    return _handle_text(text=node.value, node=node, words=words, offset_col=1)


def _handle_text(
    text: str,
    node: ast.AST,
    words: typing.Mapping[str, str],
    offset_row: int = 0,
    offset_col: int = 0,
) -> typing.Iterator[Replacement]:
    for match in REX_WORD.finditer(text):
        old_word = match.group(0)
        new_word = words.get(old_word)
        if new_word is None:
            continue
        if old_word.istitle():
            new_word = new_word.title()
        yield Replacement(
            row=node.lineno - 1 + offset_row,
            col=node.col_offset + match.start() + offset_col,
            word_from=old_word,
            word_to=new_word,
        )
