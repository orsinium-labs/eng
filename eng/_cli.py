import sys
import os
import typing
from argparse import ArgumentParser
from pathlib import Path
from ._fixer import PythonFixer, Target, TextFixer, Fixer, LiteralFixer


EXT_PY = {'.py', '.star'}
EXT_CODE = {'.go', '.toml', '.rs', '.cpp'}


def get_files(paths) -> typing.Iterator[Path]:
    for path_name in paths:
        path = Path(path_name)
        if not os.access(str(path), os.R_OK | os.W_OK):
            continue
        if path.name.startswith('.'):
            continue

        if path.is_file():
            yield path
            continue

        if path.is_dir():
            yield from get_files(path.iterdir())


def main(argv: typing.List[str]) -> int:
    parser = ArgumentParser()
    parser.add_argument('--target', default='us', choices=('us', 'uk'))
    parser.add_argument('--encoding', default='utf8')
    parser.add_argument('--exts', default='md,rst,tex,txt,py,go')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args(argv)
    exts = {'.' + ext for ext in args.exts.split(',')}

    fixed = 0
    for path in get_files(args.paths):
        path = Path(path)

        # find the best fixer based on extension
        if path.suffix not in exts:
            continue
        fixer_class: typing.Type[Fixer]
        if path.suffix in EXT_PY:
            fixer_class = PythonFixer
        elif path.suffix in EXT_CODE:
            fixer_class = LiteralFixer
        else:
            fixer_class = TextFixer

        old_content = path.read_text(encoding=args.encoding)
        fixer = fixer_class(
            content=old_content,
            target=Target(args.target),
        )
        new_content = fixer.apply()
        if new_content != old_content:
            path.write_text(new_content, encoding=args.encoding)
            fixed += 1
    return fixed


def entrypoint():
    sys.exit(main(sys.argv[1:]))
