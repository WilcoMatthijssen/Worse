import re
from classes import *


class LexerError(Exception):
    def __init__(self, char: str, postype: str, pos: int):
        """ Error for an unknown char encountered whilst lexing. """
        self.char = char
        self.postype= postype
        self.pos = pos
        super().__init__(f"Encountered unknown char \"{self.char}\" at {self.postype} {self.pos}")


# lexer :: str -> Type[Enum] -> str -> List[Token]
@deepcopy_decorator
def lexer(code: str, rules: Type[Enum] = TokenSpecies, unknowns: str = r"[^\:\=\!\+\-\(\)\,\;\?\s\w]") -> List[Token]:
    """ Finds all tokens in string and throws LexerError if an unknown is found"""
    # Check for unknowns and throw LexerError if found.
    if unknown := list(re.compile(unknowns).finditer(code)):
        raise LexerError(unknown[0][0], "char pos", unknown[0].start())

    # Create regex search func.
    joined_rules = "|".join(list(map(lambda r: f"(?P<{r.name}>{r.value})", rules)))
    search = re.compile(joined_rules).finditer

    # Create list of found tokens and return them
    return list(map(lambda m: Token(rules[m.lastgroup], m[0], m.start()), search(code)))


# morse_converter :: str -> bool -> str
@deepcopy_decorator
def morse_to_string(text: str) -> str:
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
    new_text = text.lower()

    # Check for unknowns
    if unknown := list(re.compile(r"[^-\./\s]").finditer(new_text)):
        raise LexerError(unknown[0][0], "position", unknown[0].start())

    # Convert to string
    morse_items = re.compile(r"[.\-\/]+").findall(new_text)
    result = "".join(map(lambda x: morse[x], morse_items))

    return result


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()
    print(lexer(file_content))

    morse_text = "-.. .. - / .. ... / -- --- .-. ... . -.-. --- -.. . .-.-.- / ... --- ..."
    print(morse_to_string(morse_text))
