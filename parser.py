from lexer import *
import enum


class ParserError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class AST(enum.Enum):
    OPERATION = 1
    VALUE = 2
    FUNCDEF = 3
    FUNCEXE = 4
    IFWHILE = 5
    PRINT = 6
    VAR = 7
    IDLE = 8
    ASSIGN = 9


class Node:
    def __init__(self, species):
        self.species = species


class Assign(Node):
    def __init__(self, variable, value):
        Node.__init__(self, AST.ASSIGN)
        self.variable = variable
        self.value = value

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"{self.variable.content} = {self.value}"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class Value(Node):
    def __init__(self, value):
        Node.__init__(self, AST.VALUE)
        self.value = value

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"{self.value.content}"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class Variable(Node):
    def __init__(self, name):
        Node.__init__(self, AST.VAR)
        self.name = name
    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__repr__()

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"{self.name.content}"

class FuncExe(Node):
    def __init__(self, name, params):
        Node.__init__(self, AST.FUNCEXE)
        self.name = name
        self.params: List = params

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__repr__()

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"{self.name.content} {self.params}"

class FuncDef(Node):
    def __init__(self, name, params, code):
        Node.__init__(self, AST.FUNCDEF)
        self.name = name
        self.params = params
        self.code = code

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"Define {self.name.content}({self.params}){self.code};"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class Print(Node):
    def __init__(self, value):
        Node.__init__(self, AST.PRINT)
        self.value = value

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"print {self.value}"

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__str__()


class IfWhile(Node):
    def __init__(self, expression, code, is_while=False):
        Node.__init__(self, AST.PRINT)
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
    def __init__(self,lhs, operator, rhs):
        Node.__init__(self, AST.OPERATION)
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
# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #
# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #
# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #
# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #


def parser(tokens):
    nodes, res = p(tokens)
    print("RESTANT", res)
    return nodes


def p(tokens):
    node = None

    if peek(tokens, [TokenSpecies.ID]):
        val = tokens.pop(0)
        if peek(tokens, [TokenSpecies.ASSIGN]):
            tokens.pop(0)
            pars, tokens = value(tokens)
            node = Assign(val, pars)

    if peek(tokens, [TokenSpecies.PRINT]):
        tokens.pop(0)
        if peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            pars, tokens = params(tokens)
            node = Print(pars)

    if peek(tokens, [TokenSpecies.DEF]):
        tokens.pop(0)
        if peek(tokens, [TokenSpecies.ID]):
            id = tokens.pop(0)
            if peek(tokens, [TokenSpecies.OPENBR]):
                tokens.pop(0)
                pars, tokens = defparams(tokens)
                cod, tokens = p(tokens)
                node = FuncDef(id, pars, cod)

    if peek(tokens, [TokenSpecies.WHILE, TokenSpecies.IF]):
        is_while = peek(tokens, [TokenSpecies.WHILE])
        tokens.pop(0)
        if peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            pars, tokens = value(tokens)
            if peek(tokens, [TokenSpecies.CLOSEBR]):
                tokens.pop(0)
                cod, tokens = p(tokens)
                node = IfWhile(pars, cod, is_while)

    # ---------------------------------- #

    if node:
        if peek(tokens, [TokenSpecies.END]):
            tokens.pop(0)
            other_nodes, tokens = p(tokens)
            return [node] + other_nodes, tokens
        else:
            raise ParserError("NO END CLAUSE")

    return [], tokens


def peek(tokens, species):
    return len(tokens) != 0 and tokens[0].species in species


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


def defparams(tokens):
    if peek(tokens, [TokenSpecies.ID]):
        id = Variable(tokens.pop(0))
        if peek(tokens, [TokenSpecies.SEP]):
            tokens.pop(0)
            other_ids, tokens = defparams(tokens)
            return [id]+other_ids, tokens
        elif peek(tokens, [TokenSpecies.CLOSEBR]):
            tokens.pop(0)
            return [id], tokens

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
            pars, tokens = params(tokens)
            rhs = FuncExe(rhs, pars)
        else:
            rhs = Value(rhs)

        if peek(tokens, [TokenSpecies.ADD, TokenSpecies.SUB,
                         TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            lhs, tokens = math(lhs,tokens)
            node = Operation(lhs, oper, rhs)
        elif peek(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            node = Operation(lhs, oper, rhs)
        else:
            raise ParserError("Expected operator or end of statement.")

        return node, tokens
    else:
        raise ParserError("Expected value to use in operation")


def value(tokens):
    # val = None
    # if peek(tokens, [TokenSpecies.DIGIT]):
    #     val = tokens.pop(0)
    # elif peek(tokens, [TokenSpecies.ID]):
    #     val = tokens.pop(0)
    val = tokens.pop(0) if peek(tokens, [TokenSpecies.DIGIT, TokenSpecies.ID]) else None
    # ---------------------------------- #

    if val:
        # maak func
        if val.species == TokenSpecies.ID and peek(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            pars, tokens = params(tokens)
            val = FuncExe(val, pars)

        # maak waarde
        else:
            val = Value(val)

        # maak som
        if peek(tokens, [TokenSpecies.ADD, TokenSpecies.SUB,
                         TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            val, tokens = math(val, tokens)

        # check end
        if peek(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            return val, tokens
        else:
            raise ParserError("Expected operator or end of statement.")
    else:
        raise ParserError("Expected a value but didnt get it")


if __name__ == "__main__":
    "if(a)a=11;print(a1,aa,a,a,a,a,a);;"
    tok = lexer("?fu(a)a=1;while(a)a=12+10+help(a)+20;;;", TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    #print(tok)
    print("RESULTAAT", parser(tok))

