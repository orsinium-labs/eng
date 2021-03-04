"""Change British English to American English and vice versa.
"""
from ._fixer import Target, PythonFixer, TextFixer, LiteralFixer, Fixer

__version__ = '0.1.0'
__all__ = [
    'Fixer',
    'PythonFixer',
    'TextFixer',
    'LiteralFixer',
    'Target',
]
