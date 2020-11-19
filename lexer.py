import re
from enum import Enum
from typing import Callable
from typing import List


class Tokens(Enum):
    WHILE   = "(?<!\w)while(?!\w)"
    IF      = "(?<!\w)if(?!\w)"
    PRINT   = "(?<!\w)print(?!\w)"
    ASSIGN  = "(?<![=:])\=(?![=:])"
    DEF     = "\?"
    END     = "\;"
    SEP     = "\,"
    EQUALS  = "\=\="
    NOTEQUAL= "\!\="
    GREATER = "\:\="
    LESSER  = "\=\:"
    ADD     = "\+"
    SUB     = "\-"
    OPENBR  = "\("
    CLOSEBR = "\)"
    ID      = "[a-zA-Z]\w*"
    DIGIT   = "[0-9]+"


class LexerError(Exception):
    def __init__(self, char: str, pos: int):
        """ Error for an unknown char encountered whilst lexing. """
        self.char = char
        self.pos = pos
        super().__init__(f"unknown char \"{self.char}\" found at pos {self.pos}")


class Token:
    def __init__(self, kind: Tokens, content: str, pos: int):
        """ Creates a Token containing content, pos and kind. """
        self.content = content
        self.kind = kind
        self.pos = pos

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"(<{self.content}> at pos {self.pos} is {self.kind})"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"(<{self.content}> at pos {self.pos} is {self.kind})"


def lexer(code: str, rules: Enum) -> List[Token]:
    def get_tokens(string: str, match_func: Callable[[str, int], re.Match],
                   skip_func: Callable[[str, int], re.Match], pos: int = 0) -> List[Token]:
        """ Recursively gets all keys present in string. """
        if (pos := skip.end() if (skip := skip_func(string, pos)) else pos) >= len(string):
            return []
        if m := match_func(code, pos):
            match = Token(m.lastgroup, m.group(m.lastgroup),  m.start())
            return [match] + get_tokens(code, match_func, skip_func, m.end())
        raise LexerError(string[pos], pos)

    find_whitespace = re.compile(r"[\s]+").match
    joined_rules = "|".join([f"(?P<{rule.name}>{rule.value})" for rule in rules])
    regex = re.compile(joined_rules).match
    return get_tokens(code, regex, find_whitespace)


if __name__ == "__main__":
    file = open("Worse.txt")
    filecontent = file.read()
    file.close()
    for e in lexer(filecontent, Tokens):
        print(e)


