from lexer import lexer
from classes import *


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


# is_front :: List[TokenSpecies] -> bool
@deepcopy_decorator
def is_front(tokens: List[Token], species: List[TokenSpecies]) -> bool:
    """ Returns True if first token in tokens is of the given species. """
    return len(tokens) != 0 and tokens[0].species in species


# parse_def_parameters :: List[Token] -> Tuple[Dict[str, int], List[Token]]
@deepcopy_decorator
def parse_def_parameters(tokens: List[Token]) -> Tuple[Dict[str, int], List[Token]]:
    """ Parse parameter names until an ending token is encountered. """
    params = {tokens.pop(0).content: 0} if is_front(tokens, [TokenSpecies.ID]) else {}
    if is_front(tokens, [TokenSpecies.SEP]):
        other_params, tokens = parse_def_parameters(tokens[1:])
        return {**params, **other_params}, tokens
    elif is_front(tokens, [TokenSpecies.CLOSEBR]):
        return params, tokens
    else:
        raise ParserError("Parameters", tokens[0] if len(tokens) != 0 else None)


# get_or_riot :: List[Token] -> TokenSpecies -> Tuple[Token, List[Token]]
@deepcopy_decorator
def get_or_riot(tokens: List[Token], species: TokenSpecies) -> Tuple[Token, List[Token]]:
    """ Returns a token if its the wanted species and otherwise it throws an error. """
    if is_front(tokens, [species]):
        return tokens[0], tokens[1:]
    raise ParserError(species.name, tokens[0] if tokens else None)


# parser :: List[Token] -> List[FuncDefNode]
@deepcopy_decorator
def parser(tokens: List[Token]) -> List[FuncDefNode]:
    """ Parse functions until no tokens are left. """
    _,     tokens = get_or_riot(tokens, TokenSpecies.DEF)
    name,  tokens = get_or_riot(tokens, TokenSpecies.ID)
    _,     tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
    param, tokens = parse_def_parameters(tokens)
    _,     tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    instr, tokens = parse_instructions(tokens)
    _,     tokens = get_or_riot(tokens, TokenSpecies.END)

    function_define = [FuncDefNode(name, param, instr)]
    return function_define + parser(tokens) if len(tokens) != 0 else function_define


# parse_instructions :: List[Token] -> Tuple[List[Type[ActionNode]], List[Token]]
@deepcopy_decorator
def parse_instructions(tokens: List[Token]) -> Tuple[List[Type[ActionNode]], List[Token]]:
    """ Parse instructions until a final ending token is encountered. """
    if is_front(tokens, [TokenSpecies.ID]):
        node, tokens = _parse_assign(tokens)
    elif is_front(tokens, [TokenSpecies.PRINT]):
        node, tokens = _parse_print(tokens)
    elif is_front(tokens, [TokenSpecies.WHILE, TokenSpecies.IF]):
        node, tokens = _parse_loop(tokens)
    else:
        return [], tokens

    _, tokens = get_or_riot(tokens, TokenSpecies.END)
    other_nodes, tokens = parse_instructions(tokens)
    return [node] + other_nodes, tokens


def _parse_assign(tokens):
    name, *tokens = tokens
    _, tokens = get_or_riot(tokens, TokenSpecies.ASSIGN)
    value, tokens = parse_value(tokens)
    node = AssignNode(name, value)
    return node, tokens


def _parse_loop(tokens):
    is_while = TokenSpecies.WHILE == tokens[0].species
    _,            tokens = get_or_riot(tokens[1:], TokenSpecies.OPENBR)
    parameters,   tokens = parse_value(tokens)
    _,            tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    instructions, tokens = parse_instructions(tokens)
    return IfWhileNode(parameters, instructions, is_while), tokens


def _parse_print(tokens):
    _,       *tokens = tokens
    opened,   tokens = get_or_riot(tokens, TokenSpecies.OPENBR)
    elements, tokens = parse_params(tokens)
    return PrintNode(elements, opened.pos), tokens


# parse_params :: List[Token] -> Tuple[List[Type[ValueNode]], List[Token]]
@deepcopy_decorator
def parse_params(tokens: List[Token]) -> Tuple[List[Type[ValueNode]], List[Token]]:
    """ Parse values until an ending token is encountered. """
    val, tokens = parse_value(tokens)
    if is_front(tokens, [TokenSpecies.SEP]):
        _, *tokens = tokens
        other_val, tokens = parse_params(tokens)
        return [val] + other_val, tokens
    _, tokens = get_or_riot(tokens, TokenSpecies.CLOSEBR)
    return [val], tokens


# parse_value :: List[Token] -> Token -> Optional[Type[ValueNode]] -> Tuple[Type[Node], List[Token]]
@deepcopy_decorator
def parse_value(tokens: List[Token], operation: Optional[Token] = None, lhs: Optional[Type[ValueNode]] = None) -> Tuple[Type[ValueNode], List[Token]]:
    """ Parse value until an ending token is encountered. """
    val, tokens = _parse_initial_value(tokens)
    val, tokens = _parse_operation(tokens, operation, lhs, val)
    if is_front(tokens, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
        return val, tokens
    raise ParserError(TokenSpecies.END.name, tokens[0] if len(tokens) != 0 else None)

def _parse_operation(tokens, operation, lhs, val):
    add_sub     = [TokenSpecies.ADD,      TokenSpecies.SUB]
    div_mul     = [TokenSpecies.DIV,      TokenSpecies.MUL]
    ne_ge_eq_le = [TokenSpecies.NOTEQUAL, TokenSpecies.GREATER, TokenSpecies.EQUALS, TokenSpecies.LESSER]
    if is_front(tokens, ne_ge_eq_le + div_mul) and operation is not None and operation.species in add_sub + div_mul:
        rhs, tokens = parse_value(tokens[1:], tokens[0], val)
        val = OperationNode(lhs, operation, rhs)
    else:
        val = OperationNode(lhs, operation, val) if lhs else val
        if is_front(tokens, add_sub + div_mul + ne_ge_eq_le):
            val, tokens = parse_value(tokens[1:], tokens[0], val)
    return val, tokens

def _parse_initial_value(tokens):
    if is_front(tokens, [TokenSpecies.DIGIT]):
        val, tokens = _parse_int(tokens)
    elif is_front(tokens, [TokenSpecies.ID]) and is_front(tokens[1:], [TokenSpecies.OPENBR]):
        val, tokens = _parse_func_exe(tokens)
    elif is_front(tokens, [TokenSpecies.ID]):
        val, tokens = _parse_variable(tokens)
    else:
        raise ParserError("value, variable or function", tokens[0] if tokens else None)
    return val, tokens

def _parse_int(tokens):
    value_token, *tokens = tokens
    val = IntNode(value_token)
    return val, tokens

def _parse_variable(tokens):
    name, *tokens = tokens
    val = VariableNode(name)
    return val, tokens

def _parse_func_exe(tokens):
    name = tokens[0]
    if is_front(tokens[2:], [TokenSpecies.CLOSEBR]):
        tokens = tokens[3:]
        val = FuncExeNode(name, [])
    else:
        pars, tokens = parse_params(tokens[2:])
        val = FuncExeNode(name, pars)
    return val, tokens


import pathlib
if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text()
    tokenized_code = lexer(file_content)
    print(parser(tokenized_code))

