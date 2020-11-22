import re
from enum import Enum
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
        super().__init__(f"Encountered unknown char \"{self.char}\" at pos {self.pos}")


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


suck_it_jan = lambda code, rules: list(map(lambda m: Token(m.lastgroup, m.group(m.lastgroup), m.start()), re.compile("|".join(list(map(lambda r: f"(?P<{r.name}>{r.value})", rules)))).finditer(code)))


def lexer(code: str, rules: Enum, unknowns: str) -> List[Token]:
    """ Finds all tokens in string and throws error if an unknown is found"""
    # Check for unknowns
    if unknown := list(re.compile(unknowns).finditer(code)):
        raise LexerError(unknown[0][0], unknown[0].start())

    # Create regex search func
    joined_rules = "|".join(list(map(lambda r: f"(?P<{r.name}>{r.value})", rules)))
    search = re.compile(joined_rules).finditer

    # Create list of found tokens and return them
    return list(map(lambda m: Token(m.lastgroup, m[0], m.start()), search(code)))


def morse_to_string(morse):
    morse_dict = {
         ".-":      "a",
         "-...":    "b",
         "-.-.":    "c",
         "-..":     "d",
         ".":       "e",
         "..-.":    "f",
         "--.":     "g",
         "....":    "h",
         "..":      "i",
         ".---":    "j",
         "-.-":     "k",
         ".-..":    "l",
         "--":      "m",
         "-.":      "n",
         "---":     "o",
         ".--.":    "p",
         "--.-":    "q",
         ".-.":     "r",
         "...":     "s",
         "-":       "t",
         "..-":     "u",
         "... -":   "v",
         ".--":     "w",
         "-..-":    "x",
         "-.--":    "y",
         "--..":    "z",
         "-----":   "0",
         ".----":   "1",
         "..---":   "2",
         "...--":   "3",
         "....-":   "4",
         ".....":   "5",
         "-....":   "6",
         "--...":   "7",
         "---..":   "8",
         "----.":   "9",
         ".-.-.-":  ".",
         "-..--":   ",",
         "..--..":  "?",
         "-.-.--":  "!",
         "-....-":  "-",
         "-..-.":   "/",
         "---...":  ":",
         ".----.":  "'",
         "-.--.-":  ")",
         "-.-.-":   ";",
         "-.--.":   "(",
         "-...-":   "=",
         ".--.-.":  "@",
         ".–...":   "&",
         "/":       " ",
    }
    if unknown := list(re.compile(r"[^-\./\s]").finditer(morse)):
        raise LexerError(unknown[0][0], unknown[0].start())
    return "".join(map(lambda x: morse_dict[x] , re.compile(r"(?<![.\-/])[.\-/]+").findall(morse)))


if __name__ == "__main__":
    file = open("Worse.txt")
    filecontent = file.read()
    file.close()
    print(lexer(filecontent, Tokens, "[^\:\=\!\+\-\(\)\,\;\?\s\w]"))
    q = ".--- .. .--- / --- . - .-.. ..- .-.. / --.. ..- .. --. / .--- . / -- --- . -.. . .-."
    print(morse_to_string(q))




