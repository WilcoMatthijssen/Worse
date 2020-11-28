from lexer import *
from enum import Enum


class ParserError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Node:
    def __init__(self):
        pass


class Assign(Node):
    def __init__(self, variable, value):
        Node.__init__(self)
        self.variable = variable
        self.value = value

    def __str__(self) -> str:
        return f"{self.variable.content} = {self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class Value(Node):
    def __init__(self, value):
        Node.__init__(self)
        self.value = value

    def __str__(self) -> str:
        return f"{self.value.content}"

    def __repr__(self) -> str:
        return self.__str__()


class Variable(Node):
    def __init__(self, name):
        Node.__init__(self)
        self.name = name

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name.content}"


class FuncExe(Node):
    def __init__(self, name, params):
        Node.__init__(self)
        self.name = name
        self.params: List = params

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name.content} {self.params}"


class FuncDef(Node):
    def __init__(self, name, params, code):
        Node.__init__(self)
        self.name = name
        self.params = params
        self.code = code

    def __str__(self) -> str:
        return f"Define {self.name.content}({self.params}){self.code};"

    def __repr__(self) -> str:
        return self.__str__()


class Print(Node):
    def __init__(self, value):
        Node.__init__(self)
        self.value = value

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"print {self.value}"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class IfWhile(Node):
    def __init__(self, expression, code, is_while=False):
        Node.__init__(self)
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
    def __init__(self, lhs, operator, rhs):
        Node.__init__(self)
        self.operator = operator
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"({self.lhs} {self.operator.species.name} {self.rhs})"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #

def peek(tokens, species):
    return len(tokens) != 0 and tokens[0].species in species


def get_def_parameters(tokens):
    params = [Variable(tokens.pop(0))] if peek(tokens, [TokenSpecies.ID]) else []
    if peek(tokens, [TokenSpecies.SEP]):
        other_params, tokens = get_def_parameters(tokens[1:])
        return params + other_params, tokens
    elif peek(tokens, [TokenSpecies.CLOSEBR]):
        return params, tokens
    else:
        raise ParserError("EXPECTED PARAMS U FUCKING DOG")


def get_or_riot(tokens, species):
    if len(tokens) != 0:
        if (token := tokens.pop(0)).species == species:
            return token, tokens
        else:
            raise ParserError(f"EXPECTED {species} BUT GOT {token}")
    else:
        raise ParserError(f"EXPECTED {species} BUT GOT NOTHING")


def parser(tokens):
    _, tokens = get_or_riot(tokens, TokenSpecies.DEF)
    name, tokens = get_or_riot(tokens, TokenSpecies.ID)
    _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
    param, tokens = get_def_parameters(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    instr, tokens = get_instructions(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.END)

    function = [FuncDef(name, param, instr)]
    return function + parser(tokens) if len(tokens) != 0 else function


def get_instructions(tokens):
    node = None
    if peek(tokens, [TokenSpecies.ID]):
        val = tokens.pop(0)
        _, tokens = get_or_riot(tokens, TokenSpecies.ASSIGN)
        pars, tokens = value(tokens)
        node = Assign(val, pars)

    elif peek(tokens, [TokenSpecies.PRINT]):
        tokens.pop(0)
        _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)

        pars, tokens = params(tokens)
        node = Print(pars)

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


def params(tokens):
    val, tokens = value(tokens)
    if peek(tokens, [TokenSpecies.SEP]):
        tokens.pop(0)
        other_vals, tokens = params(tokens)
        return [val] + other_vals, tokens

    if peek(tokens, [TokenSpecies.CLOSEBR]):
        tokens = tokens[1:]
        return [val], tokens

    raise ParserError("Params not ended properly")


def math(lhs, tokens):
    oper = tokens.pop(0)
    rhs = tokens.pop(0) if peek(tokens, [TokenSpecies.DIGIT, TokenSpecies.ID]) else None

    # if peek(tokens, [TokenSpecies.DIGIT]):
    #     rhs = tokens.pop(0)
    # elif peek(tokens, [TokenSpecies.ID]):
    #     rhs = tokens.pop(0)
    # else:
    #     raise ParserError("Expected value to use in operation")

    if rhs:
        if rhs.species == TokenSpecies.ID and peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            if peek(tokens, [TokenSpecies.CLOSEBR]):
                tokens.pop(0)
                rhs = FuncExe(rhs, [])
            else:
                pars, tokens = params(tokens)
                rhs = FuncExe(rhs, pars)
        else:
            rhs = Value(rhs)

        if peek(tokens, [TokenSpecies.ADD, TokenSpecies.SUB,
                         TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            lhs, tokens = math(lhs, tokens)
            node = Operation(lhs, oper, rhs)
        elif peek(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            node = Operation(lhs, oper, rhs)
        else:
            raise ParserError("Expected operator or end of statement.")

        return node, tokens
    else:
        raise ParserError("Expected value to use in operation")


def value(tokens):
    val = tokens.pop(0) if peek(tokens, [TokenSpecies.DIGIT, TokenSpecies.ID]) else None

    if val:
        if val.species == TokenSpecies.ID and peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            if peek(tokens, [TokenSpecies.CLOSEBR]):
                tokens.pop(0)
                val = FuncExe(val, [])
            else:
                pars, tokens = params(tokens)
                val = FuncExe(val, pars)
        else:
            val = Value(val)

        if peek(tokens, [TokenSpecies.ADD, TokenSpecies.SUB,
                         TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            val, tokens = math(val, tokens)

        if peek(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            return val, tokens
        else:
            raise ParserError("Expected operator or end of statement.")
    else:
        raise ParserError("Expected a value but didnt get it")


if __name__ == "__main__":
    file = open("Worse.txt")
    filecontent = file.read()
    file.close()
    "if(a)a=11;print(a1,aa,a,a,a,a,a);;"
    "?fu(a)a=1;while(a)a=12+10+help(a)+20;;;"
    tok = lexer(filecontent, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    result = parser(tok)
    for r in result:
        print(r)
