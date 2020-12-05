import re
from enum import Enum
from typing import List, Type
from functools import reduce


class TokenSpecies(Enum):
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
    def __init__(self, char: str, postype: str, pos: int):
        """ Error for an unknown char encountered whilst lexing. """
        self.char = char
        self.postype= postype
        self.pos = pos
        super().__init__(f"Encountered unknown char \"{self.char}\" at {self.postype} {self.pos}")


class Token:
    def __init__(self, species: Type[Enum], content: str, pos: int):
        """ Creates a Token containing content, pos and kind. """
        self.content = content
        self.species = species
        self.pos = pos

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__repr__()

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"(\"{self.content}\", {self.pos}, {self.species})"


def lexer(code: str, rules: Type[Enum], unknowns: str) -> List[Token]:
    """ Finds all tokens in string and throws LexerError if an unknown is found"""
    # Check for unknowns and throw LexerError if found.
    if unknown := list(re.compile(unknowns).finditer(code)):
        raise LexerError(unknown[0][0], "char pos", unknown[0].start())

    # Create regex search func.
    joined_rules = "|".join(list(map(lambda r: f"(?P<{r.name}>{r.value})", rules)))
    search = re.compile(joined_rules).finditer

    # Create list of found tokens and return them
    return list(map(lambda m: Token(rules[m.lastgroup], m[0], m.start()), search(code)))


def morse_converter(text, is_morse=True):
    """ Converts text to morse when is_morse is False and converts morse text to text if is_morse is True. """
    morse = {
        ".-":   "a",
        "-...": "b",
        "-.-.": "c",
        "-..":  "d",
        ".":    "e",
        "..-.": "f",
        "--.":  "g",
        "....": "h",
        "..":   "i",
        ".---": "j",
        "-.-":  "k",
        ".-..": "l",
        "--":   "m",
        "-.":   "n",
        "---":  "o",
        ".--.": "p",
        "--.-": "q",
        ".-.":  "r",
        "...":  "s",
        "-":    "t",
        "..-":  "u",
        "...-": "v",
        ".--":  "w",
        "-..-": "x",
        "-.--": "y",
        "--..": "z",
        "-----": "0",
        ".----": "1",
        "..---": "2",
        "...--": "3",
        "....-": "4",
        ".....": "5",
        "-....": "6",
        "--...": "7",
        "---..": "8",
        "----.": "9",

        ".-.-.-": ".",
        "--..--": ",",
        "..--..": "?",
        ".----.": "'",
        "-.-.--": "!",
        "-..-.":  "/",

        "-.--.-": ")",
        "-.--.":  "(",
        ".–...":  "&",
        "---...": ":",
        "-.-.-.": ";",
        "-...-":  "=",

        ".-.-.":  "+",
        "-....-": "-",
        "..--.-": "_",
        ".--.-.": "@",
        "/":      " ",
        "\n":     "\n",
        "\t":     "\t"

    }
    text = text.lower()
    if is_morse:
        # Convert morse to text
        if unknown := list(re.compile(r"[^-\./\s]").finditer(text)):
            raise LexerError(unknown[0][0], "position", unknown[0].start())
        morse_items = re.compile(r"(?<![.\-/])[\.\t\n\-/]+").findall(text)
        result = "".join(map(lambda x: morse[x], morse_items))

    else:
        # Convert text to morse
        rv_morse = dict(map(lambda kv: (kv[1], (kv[0])), morse.items()))
        # result = " ".join(map(lambda ch: rv_morse[ch] if ch in rv_morse.keys() else ch, text))
        result = reduce(lambda total, ch: " ".join((total, rv_morse[ch] if ch in rv_morse.keys() else ch)), text, "")

    return result


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()
    print(lexer(file_content, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]"))

    q = ".--- .. .--- / --- . - .-.. ..- .-.. / --.. ..- .. --. / .--- . / -- --- . -.. . .-."
    print(morse_converter(q, False))
