from lexer import lexer, morse_converter, LexerError
from parse import parser, ParserError
from runner import runner, RunnerError
from compiler import compiler, CompilerError
from classes import *


# worse :: str -> bool -> bool -> Optional[str]
@deepcopy_decorator
def worse(text: str, is_morse: bool, to_compile: bool) -> Optional[str]:
    """ Interprets text as Worse code. """
    try:
        normal_text = morse_converter(text) if is_morse else text
        tokens = lexer(normal_text)
        ast = parser(tokens)

        return compiler(ast) if to_compile else runner(ast)

    except LexerError as e:
        print(f"Failed lexing because: {e}")

    except ParserError as e:
        print(f"Failed parsing because: {e}")

    except RunnerError as e:
        print(f"Failed running because: {e}")

    except CompilerError as e:
        print(f"Failed compiling because: {e}")


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    print(worse(file_content, False, False))
