"""
Parser for the Worse programming language
"""


import pathlib
from typing import Tuple, Dict, List, Optional, Type
from lexer import lexer
import classes as cl
from classes import TokenSpecies as TS


class ParserError(Exception):
    """ Error for when something doesnt go as expected whilst parsing. """

    def __init__(self, wanted: str, gotten: Optional[cl.Token]):
        self.wanted = wanted
        if gotten:
            self.gotten_content = gotten.content
            self.gotten_type = gotten.species.name
            self.position = gotten.pos
            super().__init__(f"Expected {self.wanted}, but got {self.gotten_content}"
                             f" which is a(n) {self.gotten_type}, at character position {self.position}.")
        else:
            super().__init__(
                f"Expected {self.wanted}, but got nothing because its at the end of the file.")


def is_front(tokens: List[cl.Token], species: List[TS]) -> bool:
    """ is_front :: List[TS] -> boolr
    Returns True if first token in tokens is of the given species. """
    return len(tokens) != 0 and tokens[0].species in species


def parse_def_parameters(tokens: List[cl.Token]) -> Tuple[Dict[str, int], List[cl.Token]]:
    """ Parse parameter names until an ending token is encountered. """
    params = {tokens.pop(0).content: 0} if is_front(
        tokens, [TS.ID]) else {}
    if is_front(tokens, [TS.SEP]):
        other_params, tokens = parse_def_parameters(tokens[1:])
        return {**params, **other_params}, tokens
    elif is_front(tokens, [TS.CLOSEBR]):
        return params, tokens
    raise ParserError("Parameters", tokens[0] if len(tokens) else None)


def get_or_riot(tokens: List[cl.Token], species: TS) -> Tuple[cl.Token, List[cl.Token]]:
    """ get_or_riot :: List[Token] -> TS -> Tuple[Token, List[Token]]
    Returns a token if its the wanted species and otherwise it throws an error. """
    if is_front(tokens, [species]):
        return tokens[0], tokens[1:]
    raise ParserError(species.name, tokens[0] if tokens else None)



def parse_instructions(tokens: List[cl.Token]) -> Tuple[List[Type[cl.ActionNode]], List[cl.Token]]:
    """ parse_instructions :: List[Token] -> Tuple[List[Type[ActionNode]], List[Token]]
    Parse instructions until a final ending token is encountered. """
    if is_front(tokens, [TS.ID]):
        node, tokens = _parse_assign(tokens)
    elif is_front(tokens, [TS.PRINT]):
        node, tokens = _parse_print(tokens)
    elif is_front(tokens, [TS.WHILE, TS.IF]):
        node, tokens = _parse_loop(tokens)
    else:
        return [], tokens

    _, tokens = get_or_riot(tokens, TS.END)
    other_nodes, tokens = parse_instructions(tokens)
    return [node] + other_nodes, tokens


def parse_params(tokens: List[cl.Token]) -> Tuple[List[Type[cl.ValueNode]], List[cl.Token]]:
    """ parse_params :: List[Token] -> Tuple[List[Type[ValueNode]], List[Token]] 
    Parse values until an ending token is encountered. """
    val, tokens = parse_value(tokens)
    if is_front(tokens, [TS.SEP]):
        other_val, tokens = parse_params(tokens[1:])
        return [val] + other_val, tokens
    _, tokens = get_or_riot(tokens, TS.CLOSEBR)
    return [val], tokens


def _parse_assign(tokens):
    name, *tokens = tokens
    _,     tokens = get_or_riot(tokens, TS.ASSIGN)
    value, tokens = parse_value(tokens)
    node = cl.AssignNode(name, value)
    return node, tokens


def _parse_loop(tokens):
    is_while = TS.WHILE == tokens[0].species
    _,            tokens = get_or_riot(tokens[1:], TS.OPENBR)
    parameters,   tokens = parse_value(tokens)
    _,            tokens = get_or_riot(tokens, TS.CLOSEBR)
    instructions, tokens = parse_instructions(tokens)
    return cl.IfWhileNode(parameters, instructions, is_while), tokens


def _parse_print(tokens):
    _,       *tokens = tokens
    opened,   tokens = get_or_riot(tokens, TS.OPENBR)
    elements, tokens = parse_params(tokens)
    return cl.PrintNode(elements, opened.pos), tokens


# def parse_params(tokens: List[Token]):
#     if is_front(tokens, TS.CLOSEBR):
#         return [], tokens[1:]
#     val, tokens = parse_value(tokens)
#     if is_front(tokens, [TS.SEP]):
#         other_val, tokens = parse_params(tokens[1:])
#         return [val] + other_val, tokens
# def _parse_func_exe(tokens):
#     name,       tokens = get_or_riot(tokens, TS.ID)
#     parameters, tokens = parse_params(tokens[1:])
#     return FuncExeNode(name, parameters), tokens
def _parse_func_exe(tokens):
    name = tokens[0]
    if is_front(tokens[2:], [TS.CLOSEBR]):
        tokens = tokens[3:]
        pars = []
    else:
        pars, tokens = parse_params(tokens[2:])
    return cl.FuncExeNode(name, pars), tokens


# parse_value :: List[Token] -> Token -> Optional[Type[ValueNode]] -> Tuple[Type[Node], List[Token]]
def parse_value(tokens: List[cl.Token], operation: Optional[cl.Token] = None, lhs: Optional[Type[cl.ValueNode]] = None) -> Tuple[Type[cl.ValueNode], List[cl.Token]]:
    """ Parse value until an ending token is encountered. """
    val, tokens = _parse_initial_value(tokens)
    val, tokens = _parse_operation(tokens, operation, lhs, val)
    if is_front(tokens, [TS.SEP, TS.CLOSEBR, TS.END]):
        return val, tokens
    raise ParserError(TS.END.name, tokens[0] if len(tokens) else None)


def _parse_operation(tokens, operation, lhs, val):
    add_sub = [TS.ADD,      TS.SUB]
    div_mul = [TS.DIV,      TS.MUL]
    ne_ge_eq_le = [TS.NOTEQUAL, TS.GREATER,
                   TS.EQUALS, TS.LESSER]
    if is_front(tokens, ne_ge_eq_le + div_mul) and operation is not None and operation.species in add_sub + div_mul:
        rhs, tokens = parse_value(tokens[1:], tokens[0], val)
        val = cl.OperationNode(lhs, operation, rhs)
    else:
        val = cl.OperationNode(lhs, operation, val) if lhs else val
        if is_front(tokens, add_sub + div_mul + ne_ge_eq_le):
            val, tokens = parse_value(tokens[1:], tokens[0], val)
    return val, tokens


def _parse_initial_value(tokens):
    if is_front(tokens, [TS.DIGIT]):
        return create_node_and_return_remainder(tokens, cl.IntNode)
    elif is_front(tokens, [TS.ID]) and is_front(tokens[1:], [TS.OPENBR]):
        return _parse_func_exe(tokens)
    elif is_front(tokens, [TS.ID]):
        return create_node_and_return_remainder(tokens, cl.VariableNode)
    raise ParserError("value, variable or function", tokens[0] if tokens else None)


def create_node_and_return_remainder(tokens, node):
    return node(tokens[0]), tokens[1:]


def parser(tokens: List[cl.Token]) -> List[cl.FuncDefNode]:
    """ parser :: List[Token] -> List[FuncDefNode]
    Parse functions until no tokens are left. """
    _,     tokens = get_or_riot(tokens, TS.DEF)
    name,  tokens = get_or_riot(tokens, TS.ID)
    _,     tokens = get_or_riot(tokens, TS.OPENBR)
    param, tokens = parse_def_parameters(tokens)
    _,     tokens = get_or_riot(tokens, TS.CLOSEBR)
    instr, tokens = parse_instructions(tokens)
    _,     tokens = get_or_riot(tokens, TS.END)

    function_define = [cl.FuncDefNode(name, param, instr)]
    return function_define + (parser(tokens) if len(tokens) else [])


if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text(encoding='utf-8')
    tokenized_code = list(lexer(file_content))
    print(parser(tokenized_code))
