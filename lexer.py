import re
import pathlib
from enum import Enum
from typing import Iterable, Type
from classes import TokenSpecies, Token


class LexerError(Exception):
    def __init__(self, char: str, postype: str, pos: int):
        """ Error for an unknown char encountered whilst lexing. """
        super().__init__(f"Encountered unknown char \"{char}\" at {postype} {pos}")


# lexer :: str -> Type[Enum] -> str -> List[Token]
def lexer(code: str, rules: Type[Enum] = TokenSpecies, unknowns: str = r"[^\:\=\!\+\-\(\)\,\;\?\s\w]") -> Iterable[Token]:
    """ Finds all tokens in string and throws LexerError if an unknown is found"""
    # Check for unknowns and throw LexerError if found.
    if unknown := list(re.compile(unknowns).finditer(code)):
        raise LexerError(unknown[0][0], "char pos", unknown[0].start())

    # Create regex search func.
    joined_rules = "|".join(map(lambda rule: f"(?P<{rule.name}>{rule.value})", rules))
    search = re.compile(joined_rules).finditer

    # Create list of found tokens and return them
    return map(lambda m: Token(rules[m.lastgroup], m[0], m.start()), search(code))


if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text("utf-8")
    print(list(lexer(file_content)))
