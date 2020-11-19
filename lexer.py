from enum import Enum
from typing import Callable


class TokenType(Enum):
    EOF = 1
    INT = 2
    NONE = 3
    IF = 4
    ID = 5
    WHILE = 6
    OP = 7
    DEF = 8
    SEP =9
    END = 10
    PRINT = 11
    ASSIGN = 12
    OPENBR =13
    CLOSEBR = 14


class Token:
    def __init__(self):
        self.type: TokenType = TokenType.NONE
        self.value: str = ""

    def __str__(self):
        return f"\n({self.type}  \"{self.value}\")"

    def __repr__(self):
        return f"\n({self.type}  \"{self.value}\")"


def Lexer(code: str) -> (Token, str):
    def identify(value):
        keywords = {
            "?": TokenType.DEF,
            ".": TokenType.END,
            ",": TokenType.SEP,
            "+": TokenType.OP,
            "-": TokenType.OP,
            "=": TokenType.ASSIGN,
            "(": TokenType.OPENBR,
            ")": TokenType.CLOSEBR,
            "if": TokenType.IF,
            "while": TokenType.WHILE,
            "print": TokenType.PRINT,
        }
        type = TokenType.NONE
        if value in keywords:
            type = keywords[value]
        elif value[0].isalpha():
            type = TokenType.ID
        elif value[0].isdigit():
            type = TokenType.INT
        return type

    def aCheck(t: Token, code: str, check: Callable) -> (Token, str):
        if len(code) > 0:
            if check(code[0]):
                t.value += code[0]
                code = code[1:]
                return aCheck(t, code, check)
        t.type = identify(t.value)
        return t, code

    def getNextKey(t: Token, code: str) -> (Token, str):
        if code == "" and t.value == "":
            t.type = TokenType.EOF
            return t, code
        t.value = code[0]
        code = code[1:]
        if t.value.isdigit():
            return aCheck(t, code, lambda c: c.isdigit())

        elif t.value.isalpha():
            return aCheck(t, code, lambda c: c.isdigit() or c.isalpha())

        elif t.value in "?+-/.,=()":
            t.type = identify(t.value)
            return t, code

        else:
            t.value = ""
            return getNextKey(t, code)


    t, code = getNextKey(Token(), code)
    if len(code) > 0:
        return [t] + Lexer(code)
    return [t]

if __name__ == "__main__":
    file = open("Worse.txt")
    code = file.read()
    file.close()

    print(Lexer(code))



