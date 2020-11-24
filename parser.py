
import lexer
import enum
from lexer import *

"""
assign = var assign val
operation = val operator val
func = id openbr val sep val closebr
val = var|int|func|operation
ifwhile = if|while openbr val closebr print|ifwhile|assign end
print = print open br val close br
var = id
int = int
"""
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
    ASSIGN =9


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
        return f"{self.name.content}{self.params}"

class FuncDef(Node):
    def __init__(self, name, params, code):
        Node.__init__(self, AST.FUNCDEF)
        self.name = name
        self.params = params
        self.code = code

class Print(Node):
    def __init__(self, value):
        Node.__init__(self, AST.PRINT)
        self.value = value

class IfWhile(Node):
    def __init__(self, expression, code, is_while=False):
        Node.__init__(self, AST.PRINT)
        self.expression = expression
        self.code = code
        self.is_while = is_while


class Operation(Node):
    def __init__(self,lhs, operator, rhs):
        Node.__init__(self, AST.OPERATION)
        self.operator = operator
        self.rhs = rhs
        self.lhs = lhs


"""
assign = id assign waarde end

waarde = id | digit
        openbr -> func, operator -> som, end or sep.
        

"""

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.next_token = None
        self.advance()
        self.nodes = [self.begin()]

    def not_a_loop(self, expression, action):
        if expression():
            return [action()] + self.not_a_loop(expression, action)
        return []

    def advance(self):
        if len(self.tokens) != 0:
            old = self.next_token
            self.next_token, *self.tokens = self.tokens
            return old
        raise ParserError(len(self.tokens))

    def begin(self):
        curr = self.advance()
        if curr.species == TokenSpecies.ID:
            return self.assign(curr)

    def params(self):
        print("param", self.next_token)
        param = self.value()
        print("param", self.next_token)
        curr =self.advance()
        if curr.species == TokenSpecies.SEP:
            return [param] + self.params()
        if curr.species == TokenSpecies.CLOSEBR:
            return [param]
        raise ParserError("Params not ended properly")

    def assign(self, id_var):
        print("assign", self.next_token)
        curr = self.advance()
        if curr.species == TokenSpecies.ASSIGN:
            ass = Assign(id_var, self.value())
            if self.next_token.species == TokenSpecies.END:
                return ass
        raise ParserError("Expected assignment")

    def value(self):
        print("value", self.next_token)
        start = self.advance()
        if start.species in (TokenSpecies.DIGIT, TokenSpecies.ID):
            if start.species == TokenSpecies.ID and self.next_token.species == TokenSpecies.OPENBR:
                val = self.func(start)
            else:
                val = Value(start)
            if self.next_token.species in (TokenSpecies.END, TokenSpecies.SEP, TokenSpecies.CLOSEBR):
                return val
            raise ParserError("Expected end of statement")

        raise ParserError("Expected value")


    def func(self, func_var):
        print("func", self.next_token)

        t = self.advance()

        if self.next_token.species == TokenSpecies.CLOSEBR:
            return FuncExe(func_var, [])
        # pars = self.not_a_loop()
        return FuncExe(func_var, self.params())





if __name__ == "__main__":
    tok = lexer("a=help(yeet(1,help(aaa)),1,1)aaa;", TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    print(tok)
    p = Parser(tok)
    print(*p.nodes)









