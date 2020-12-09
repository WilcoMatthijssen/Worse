from __future__ import annotations
from lexer import *
from typing import Tuple, Union, Dict, Optional


class ParserError(Exception):
    """ Error for when something doesnt go as expected whilst parsing. """
    def __init__(self, wanted: str, gotten: Optional[Token]):
        self.wanted = wanted
        if gotten:
            self.gotten_content = gotten.content
            self.gotten_type = gotten.species.name
            self.position = gotten.pos
            super().__init__(f"Expected {self.wanted}, but got {self.gotten_content}"
                             f" which is a(n) {self.gotten_type}, at character position {self.position}.")
        else:
            super().__init__(f"Expected {self.wanted}, but got nothing because its at the end of the file.")


class Node:
    """ Base class for nodes. """
    def __init__(self, pos: int):
        """ Init for Node. """
        self.pos = pos

    def __str__(self) -> str:
        return f"Empty base Node"

    def __repr__(self) -> str:
        return self.__str__()


class ValueNode(Node):
    def __init__(self, value: Token):
        """ Init for ValueNode. """
        Node.__init__(self, value.pos)
        self.value = value.content

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class VariableNode(Node):
    def __init__(self, name: Token):
        """ Init for VariableNode. """
        Node.__init__(self, name.pos)
        self.name = name.content

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name}"


class FuncExeNode(Node):
    def __init__(self, name: Token, params: List[Type[Node]]):
        """ Init for FuncExeNode. """
        Node.__init__(self, name.pos)
        self.name = name.content
        self.params = params

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return f"{self.name} {self.params}"


class OperationNode(Node):
    """ Init for operationNode. """
    def __init__(self, lhs: Union[FuncExeNode, VariableNode, ValueNode, OperationNode], operator: Token,
                 rhs: Union[FuncExeNode, VariableNode, ValueNode, OperationNode]):
        Node.__init__(self, operator.pos)
        self.operator = operator.species
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self) -> str:
        return f"({self.lhs} {self.operator} {self.rhs})"

    def __repr__(self) -> str:
        return self.__str__()


class AssignNode(Node):
    def __init__(self, variable: Token, value: Union[FuncExeNode, VariableNode, ValueNode, OperationNode]):
        """ Init for AssignNode. """
        Node.__init__(self, variable.pos)
        self.name = variable.content
        self.value = value

    def __str__(self) -> str:
        return f"{self.name} = {self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class PrintNode(Node):
    def __init__(self, value: List[Union[FuncExeNode, VariableNode, ValueNode, OperationNode]], pos: int):
        """ Init for PrintNode. """
        Node.__init__(self, pos)
        self.value = value

    def __str__(self) -> str:
        return f"print {self.value}"

    def __repr__(self) -> str:
        return self.__str__()


class IfWhileNode(Node):
    def __init__(self, condition: Union[OperationNode, VariableNode, ValueNode, FuncExeNode],
                 actions: List[Union[AssignNode, PrintNode, IfWhileNode]], is_while: bool):
        """ Init for IfWhileNode. """
        Node.__init__(self, condition.pos)
        self.condition = condition
        self.actions = actions
        self.is_while = is_while

    def __str__(self) -> str:
        loop = "while" if self.is_while else "if"
        return f"({loop}({self.condition}) {self.actions})"

    def __repr__(self) -> str:
        return self.__str__()


class FuncDefNode(Node):
    def __init__(self, name: Token, params: Dict[str, int], actions: List[Union[AssignNode, PrintNode, IfWhileNode]]):
        """ Init for FuncDefNode. """
        Node.__init__(self, name.pos)
        self.name = name.content
        self.params = params
        self.actions = actions

    def __str__(self) -> str:
        return f"Define {self.name}({self.params}){self.actions};"

    def __repr__(self) -> str:
        return self.__str__()

# ---------------------------------- ## ---------------------------------- ## ---------------------------------- #


# is_front :: List[TokenSpecies] -> bool
def is_front(tokens: List[Token], species: List[TokenSpecies]) -> bool:
    """ Returns True if first token in tokens is of the given species. """
    return len(tokens) != 0 and tokens[0].species in species


# parse_def_parameters :: List[Token] -> Tuple[Dict[str, int], List[Token]]
def parse_def_parameters(tokens: List[Token]) -> Tuple[Dict[str, int], List[Token]]:
    """ Parse parameter names until an ending token is encountered. """
    params = {tokens.pop(0).content: 0} if is_front(tokens, [TokenSpecies.ID]) else {}
    if is_front(tokens, [TokenSpecies.SEP]):
        other_params, tokens = parse_def_parameters(tokens[1:])
        params.update(other_params)
        return params, tokens
    elif is_front(tokens, [TokenSpecies.CLOSEBR]):
        return params, tokens
    else:
        raise ParserError("Parameters", tokens.pop(0) if len(tokens) != 0 else None)


# get_or_riot :: List[Token] -> TokenSpecies -> Tuple[Token, List[Token]]
def get_or_riot(tokens: List[Token], species: TokenSpecies) -> Tuple[Token, List[Token]]:
    """ Returns a token if its the wanted species and otherwise it throws an error. """
    if len(tokens) != 0:
        if (token := tokens.pop(0)).species == species:
            return token, tokens
        else:
            raise ParserError(species.name, token)
    else:
        raise ParserError(species.name, None)


# parser :: List[Token] -> List[FuncDefNode]
def parser(tokens: List[Token]) -> List[FuncDefNode]:
    """ Parse functions until no tokens are left. """
    _, tokens = get_or_riot(tokens, TokenSpecies.DEF)
    name, tokens = get_or_riot(tokens, TokenSpecies.ID)
    _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
    param, tokens = parse_def_parameters(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    instr, tokens = parse_instructions(tokens)
    _, tokens = get_or_riot(tokens, TokenSpecies.END)

    function = [FuncDefNode(name, param, instr)]
    return function + parser(tokens) if len(tokens) != 0 else function


# parse_instructions :: List[Token] -> Tuple[List[Type[Node]], List[Token]]
def parse_instructions(tokens: List[Token]) -> Tuple[List[Type[Node]], List[Token]]:
    """ Parse instructions until a final ending token is encountered. """
    node = None
    if is_front(tokens, [TokenSpecies.ID]):
        name = tokens.pop(0)
        _, tokens = get_or_riot(tokens, TokenSpecies.ASSIGN)
        value, tokens = parse_value(tokens)
        node = AssignNode(name, value)

    elif is_front(tokens, [TokenSpecies.PRINT]):
        tokens.pop(0)
        opened, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
        elements, tokens = parse_params(tokens)
        node = PrintNode(elements, opened.pos)

    elif is_front(tokens, [TokenSpecies.WHILE, TokenSpecies.IF]):
        is_while = TokenSpecies.WHILE == tokens.pop(0).species

        _, tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
        parameters, tokens = parse_value(tokens)
        _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)

        instructions, tokens = parse_instructions(tokens)
        node = IfWhileNode(parameters, instructions, is_while)

    if node:
        _, tokens = get_or_riot(tokens, TokenSpecies.END)
        other_nodes, tokens = parse_instructions(tokens)
        return [node] + other_nodes, tokens
    return [], tokens


# parse_params :: List[Token] -> Tuple[List[Type[Node]], List[Token]]
def parse_params(tokens: List[Token]) -> Tuple[List[Type[Node]], List[Token]]:
    """ Parse values until an ending token is encountered. """
    val, tokens = parse_value(tokens)
    if is_front(tokens, [TokenSpecies.SEP]):
        tokens.pop(0)
        other_val, tokens = parse_params(tokens)
        return [val] + other_val, tokens

    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    return [val], tokens


# parse_value :: List[Token] -> Token -> Union[FuncExeNode, VariableNode, ValueNode] -> Tuple[Type[Node], List[Token]]
def parse_value(tokens: List[Token], operation: Token = None,
                 lhs: Union[FuncExeNode, VariableNode, ValueNode] = None) -> Tuple[Type[Node], List[Token]]:
    """ Parse value until an ending token is encountered. """
    val = None
    if is_front(tokens, [TokenSpecies.DIGIT]):
        val = ValueNode(tokens.pop(0))
    elif is_front(tokens, [TokenSpecies.ID]):
        name = tokens.pop(0)
        if is_front(tokens, [TokenSpecies.OPENBR]):
            tokens.pop(0)
            if is_front(tokens, [TokenSpecies.CLOSEBR]):
                tokens.pop(0)
                val = FuncExeNode(name, [])
            else:
                pars, tokens = parse_params(tokens)
                val = FuncExeNode(name, pars)
        else:
            val = VariableNode(name)

    if val:
        if lhs:
            val = OperationNode(lhs, operation, val)
        if is_front(tokens, [TokenSpecies.ADD, TokenSpecies.SUB, TokenSpecies.NOTEQUAL,
                             TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]):
            operation = tokens.pop(0)
            val, tokens = parse_value(tokens, operation, val)
        if is_front(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
            return val, tokens

        raise ParserError(TokenSpecies.END.name, tokens.pop(0) if len(tokens) != 0 else None)
    raise ParserError("ValueNode, variable or function", tokens.pop(0) if len(tokens) != 0 else None)


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    print(parser(tokenized_code))
