from lexer import *
from enum import Enum
from typing import Tuple, Union, Dict

class ParserError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Node:
    def __init__(self, pos: int):
        self.pos = pos


class Value(Node):
    def __init__(self, value: Token):
        Node.__init__(self, value.pos)
        self.value = value.content

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class Variable(Node):
    def __init__(self, name: Token):
        Node.__init__(self, name.pos)
        self.name = name.content

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}"


class FuncExe(Node):
    def __init__(self, name: Token, params: List[Type[Node]]):
        Node.__init__(self, name.pos)
        self.name = name.content
        self.params = params

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name} {self.params}"


class FuncDef(Node):
    def __init__(self, name: Token, params: Dict[str, int], code: List[Type[Node]]):
        Node.__init__(self, name.pos)
        self.name = name.content
        self.params = params
        self.code = code


    def __str__(self) -> str:
        return f"Define {self.name}({self.params}){self.code};"

    def __repr__(self) -> str:
        return self.__str__()


class Print(Node):
    def __init__(self, value: List[Type[Node]], pos: int):
        Node.__init__(self, pos)
        self.value = value

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"print {self.value}"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class IfWhile(Node):
    def __init__(self, expression: Type[Node], code: List[Type[Node]], is_while: bool):
        Node.__init__(self, expression.pos)
        self.expression = expression
        self.code = code
        self.is_while = is_while

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        loop = "while" if self.is_while else "if"
        return f"({loop}({self.expression}) {self.code})"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class Operation(Node):
    def __init__(self, lhs: Union[FuncExe, Variable, Value], operator, rhs: Union[FuncExe, Variable, Value]):
        Node.__init__(self, operator.pos)
        self.operator = operator.species
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"({self.lhs} {self.operator} {self.rhs})"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class Assign(Node):
    def __init__(self, variable: Token, value: Type[Node]):
        Node.__init__(self, variable.pos)
        self.name = variable.content
        self.value = value


    def __str__(self) -> str:
        return f"{self.name} = {self.value}"

    def __repr__(self) -> str:
        return self.__str__()


# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #

def peek(tokens: List[Token], species: List[TokenSpecies]) -> bool:
    return len(tokens) != 0 and tokens[0].species in species


def get_def_parameters(tokens: List[Token]) -> Tuple[Dict[str, int], List[Token]]:
    params = {tokens.pop(0).content: 0} if peek(tokens, [TokenSpecies.ID]) else {}
    if peek(tokens, [TokenSpecies.SEP]):
        other_params, tokens = get_def_parameters(tokens[1:])
        params.update(other_params)
        return params, tokens
    elif peek(tokens, [TokenSpecies.CLOSEBR]):
        return params, tokens
    else:
        raise ParserError("EXPECTED PARAMS U FUCKING DOG")


def get_or_riot(tokens: List[Token], species: TokenSpecies) -> Tuple[Token, List[Token]]:
    if len(tokens) != 0:
        if (token := tokens.pop(0)).species == species:
            return token, tokens
        else:
            raise ParserError(f"EXPECTED {species} BUT GOT {token}")
    else:
        raise ParserError(f"EXPECTED {species} BUT GOT NOTHING")


def parser(tokens: List[Token]) -> List[FuncDef]:
    _, tokens = get_or_riot(tokens, TokenSpecies.DEF)
    name, tokens = get_or_riot(tokens, TokenSpecies.ID)
    _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
    param, tokens = get_def_parameters(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    instr, tokens = get_instructions(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.END)

    function = [FuncDef(name, param, instr)]
    return function + parser(tokens) if len(tokens) != 0 else function


def get_instructions(tokens: List[Token]) -> Tuple[List[Type[Node]], List[Token]]:
    node = None
    if peek(tokens, [TokenSpecies.ID]):
        val = tokens.pop(0)

        _, tokens = get_or_riot(tokens, TokenSpecies.ASSIGN)

        pars, tokens = value(tokens)
        node = Assign(val, pars)

    elif peek(tokens, [TokenSpecies.PRINT]):
        tokens.pop(0)
        opened, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
        elements, tokens = params(tokens)
        node = Print(elements, opened.pos)

    elif peek(tokens, [TokenSpecies.WHILE, TokenSpecies.IF]):
        is_while = TokenSpecies.WHILE == tokens.pop(0).species

        _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
        pars, tokens = value(tokens)
        _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)

        cod, tokens = get_instructions(tokens)
        node = IfWhile(pars, cod, is_while)

    if node:
        _, tokens = get_or_riot(tokens, TokenSpecies.END)
        other_nodes, tokens = get_instructions(tokens)
        return [node] + other_nodes, tokens
    return [], tokens


def params(tokens: List[Token]) -> Tuple[List[Type[Node]], List[Token]]:
    val, tokens = value(tokens)
    if peek(tokens, [TokenSpecies.SEP]):
        tokens.pop(0)
        other_val, tokens = params(tokens)
        return [val] + other_val, tokens

    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    return [val], tokens


def value(tokens: List[Token], operation: Token = None, lhs: Union[FuncExe, Variable, Value] = None) -> Tuple[Type[Node], List[Token]]:
    val = None
    if peek(tokens, [TokenSpecies.DIGIT]):
        val = Value(tokens.pop(0))
    elif peek(tokens, [TokenSpecies.ID]):
        name = tokens.pop(0)
        if peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            if peek(tokens, [TokenSpecies.CLOSEBR]):
                tokens.pop(0)
                val = FuncExe(name, [])
            else:
                pars, tokens = params(tokens)
                val = FuncExe(name, pars)
        else:
            val = Variable(name)

    if val:
        if lhs:
            val = Operation(lhs, operation, val)
        if peek(tokens, [TokenSpecies.ADD, TokenSpecies.SUB, TokenSpecies.NOTEQUAL,
                         TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            operation = tokens.pop(0)
            val, tokens = value(tokens, operation, val)
        if peek(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            return val, tokens
        print(val)
        raise ParserError("Expected end of statement.")
    raise ParserError("Expected a value but didnt get it")


if __name__ == "__main__":
    file = open("Worse.txt")
    filecontent = file.read()
    file.close()

    tok = lexer(filecontent, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")

    ast = parser(tok)

    print(ast)
