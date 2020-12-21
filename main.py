from lexer import lexer, morse_to_string, LexerError
from parse import parser, ParserError
from runner import runner, RunnerError
from classes import *
import sys
import os


# worse :: str -> bool -> bool -> Optional[str]
@deepcopy_decorator
def worse(text: str, is_morse: bool, to_compile: bool) -> Optional[str]:
    """ Interprets text as Worse code. """
    try:
        normal_text = morse_to_string(text) if is_morse else text
        tokens = lexer(normal_text)
        ast = parser(tokens)

        return "" if to_compile else runner(ast)

    except LexerError as e:
        print(f"Failed lexing because: {e}")

    except ParserError as e:
        print(f"Failed parsing because: {e}")

    except RunnerError as e:
        print(f"Failed running because: {e}")


if __name__ == "__main__":
    _, filename, do_morse = sys.argv

    file = open(filename)
    file_content = file.read()
    file.close()

    worse(file_content, do_morse == "y", False)

