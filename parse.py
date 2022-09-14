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
        recieved = f"{gotten.species.name} at {gotten.pos}" if gotten else "nothing"
        super().__init__(f"Expected {wanted}, but recieved {recieved}.")



def is_front(tokens: List[cl.Token], species: List[TS]) -> bool:
    """ is_front :: List[TS] -> boolr
    Returns True if first token in tokens is of the given species. """
    return tokens and tokens[0].species in species


def get_or_riot(tokens: List[cl.Token], species: TS) -> Tuple[cl.Token, List[cl.Token]]:
    """ get_or_riot :: List[Token] -> TS -> Tuple[Token, List[Token]]
    Returns a token if its the wanted species and otherwise it throws an error. """
    if is_front(tokens, [species]):
        return tokens[0], tokens[1:]
    raise ParserError(species.name, tokens[0] if tokens else None)


def parse_def_parameters(tokens: List[cl.Token]) -> Tuple[Dict[str, int], List[cl.Token]]:
    """ Parse parameter names until an ending token is encountered. """
    match tuple(tokens):
        case cl.Token(TS.CLOSEBR), *remainder:
            return {}, remainder
        case cl.Token(TS.ID) as param, cl.Token(TS.CLOSEBR), *remainder:
            return {param.content: 0}, remainder
        case cl.Token(TS.ID) as param, cl.Token(TS.SEP), *remainder:
            other_params, remainder = parse_def_parameters(remainder)
            return {param.content: 0} | other_params, remainder
        case _:
            raise ParserError("Parameters", tokens[0] if tokens else None)
    return None, None # Can't reach this but Pylint will go crazy without


def parse_instructions(tokens: List[cl.Token]) -> Tuple[List[Type[cl.ActionNode]], List[cl.Token]]:
    """ parse_instructions :: List[Token] -> Tuple[List[Type[ActionNode]], List[Token]]
    Parse instructions until a final ending token is encountered. """
    match tuple(tokens):
        case cl.Token(TS.ID) as name,cl.Token(TS.ASSIGN), *remainder:
            value, tokens = parse_value(remainder)
            node = cl.AssignNode(name, value)
        case cl.Token(TS.PRINT) as name, cl.Token(TS.OPENBR), *remainder:
            elements, tokens = parse_params(remainder)
            node = cl.PrintNode(elements, name.pos)
        case cl.Token(TS.WHILE | TS.IF) as keyword, cl.Token(TS.OPENBR), *remainder:
            parameters,   tokens = parse_value(remainder)
            _,            tokens = get_or_riot(tokens, TS.CLOSEBR)
            instructions, tokens = parse_instructions(tokens)
            is_while = TS.WHILE == keyword.species
            node = cl.IfWhileNode(parameters, instructions, is_while)
        case _:
            return [], tokens

    _, tokens = get_or_riot(tokens, TS.END)
    other_nodes, tokens = parse_instructions(tokens)
    return [node] + other_nodes, tokens


def _parse_func_exe(tokens):
    match tuple(tokens):
        case cl.Token(TS.ID) as name, cl.Token(TS.OPENBR), cl.Token(TS.CLOSEBR), *rest:
            return cl.FuncExeNode(name, []), rest
        case cl.Token(TS.ID) as name, cl.Token(TS.OPENBR), *rest:
            parameters, rest = parse_params(rest)
            return cl.FuncExeNode(name, parameters), rest


def _parse_initial_value(tokens) -> Tuple[Type[cl.ValueNode], List[cl.Token]]:
    match tuple(tokens):
        case cl.Token(TS.DIGIT) as digit, *remainder:
            return cl.IntNode(digit), remainder

        case cl.Token(TS.ID), cl.Token(TS.OPENBR), *remainder:
            return _parse_func_exe(tokens)

        case cl.Token(TS.ID) as name, *remainder:
            return cl.VariableNode(name), remainder

        case _:
            raise ParserError("value, variable or function",
                                 tokens[0] if tokens else None)
    return None, None # Can't reach this but Pylint will go crazy without


def parse_params(tokens: List[cl.Token]) -> Tuple[List[Type[cl.ValueNode]], List[cl.Token]]:
    """ parse_params :: List[Token] -> Tuple[List[Type[ValueNode]], List[Token]]
    Parse values until an ending token is encountered. """
    val, tokens = parse_value(tokens)
    if is_front(tokens, [TS.SEP]):
        other_val, tokens = parse_params(tokens[1:])
        return [val] + other_val, tokens
    _, tokens = get_or_riot(tokens, TS.CLOSEBR)
    return [val], tokens


def parse_value(tokens: List[cl.Token], operation: Optional[cl.Token] = None, lhs: Optional[Type[cl.ValueNode]] = None, val = None):
    """parse value"""
    val, tokens = _parse_initial_value(tokens)
    add_sub = TS.ADD, TS.SUB
    div_mul = TS.DIV, TS.MUL
    ne_ge_eq_le = TS.NOTEQUAL, TS.GREATER, TS.EQUALS, TS.LESSER
    if is_front(tokens, ne_ge_eq_le + div_mul) and operation and operation.species in add_sub + div_mul:
        rhs, tokens = parse_value(tokens[1:], tokens[0], val)
        val = cl.OperationNode(lhs, operation, rhs)
    else:
        val = cl.OperationNode(lhs, operation, val) if lhs else val
        if is_front(tokens, add_sub + div_mul + ne_ge_eq_le):
            val, tokens = parse_value(tokens[1:], tokens[0], val)
    return val, tokens


def parser(tokens: List[cl.Token]) -> List[cl.FuncDefNode]:
    """ parser :: List[Token] -> List[FuncDefNode]
    Parse functions until no tokens are left. """
    _,     tokens = get_or_riot(tokens, TS.DEF)
    name,  tokens = get_or_riot(tokens, TS.ID)
    _,     tokens = get_or_riot(tokens, TS.OPENBR)
    param, tokens = parse_def_parameters(tokens)
    instr, tokens = parse_instructions(tokens)
    _,     tokens = get_or_riot(tokens, TS.END)
    function_define = [cl.FuncDefNode(name, param, instr)]
    return function_define + (parser(tokens) if len(tokens) else [])


if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text(encoding='utf-8')
    tokenized_code = list(lexer(file_content))
    print(parser(tokenized_code))
