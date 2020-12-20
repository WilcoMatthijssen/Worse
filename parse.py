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
    raise ParserError(species.name, tokens[0] if len(tokens) != 0 else None)


# parser :: List[Token] -> List[FuncDefNode]
@deepcopy_decorator
def parser(tokens: List[Token]) -> List[FuncDefNode]:
    """ Parse functions until no tokens are left. """
    _, tokens0 = get_or_riot(tokens, TokenSpecies.DEF)
    name, tokens1 = get_or_riot(tokens0, TokenSpecies.ID)
    _, tokens2 = get_or_riot(tokens1, TokenSpecies.OPENBR)
    param, tokens3 = parse_def_parameters(tokens2)
    _, tokens4 = get_or_riot(tokens3, TokenSpecies.CLOSEBR)
    instr, tokens5 = parse_instructions(tokens4)
    _, tokens6 = get_or_riot(tokens5, TokenSpecies.END)

    function_define = [FuncDefNode(name, param, instr)]
    return function_define + parser(tokens6) if len(tokens6) != 0 else function_define


# parse_instructions :: List[Token] -> Tuple[List[Type[ActionNode]], List[Token]]
@deepcopy_decorator
def parse_instructions(tokens: List[Token]) -> Tuple[List[Type[ActionNode]], List[Token]]:
    """ Parse instructions until a final ending token is encountered. """
    if is_front(tokens, [TokenSpecies.ID]):
        name, *tokens0 = tokens
        _, tokens1 = get_or_riot(tokens0, TokenSpecies.ASSIGN)
        value, tokens2 = parse_value(tokens1)
        node = AssignNode(name, value)

    elif is_front(tokens, [TokenSpecies.PRINT]):
        tokens0 = tokens[1:]
        opened, tokens1 = get_or_riot(tokens0, TokenSpecies.OPENBR)
        elements, tokens2 = parse_params(tokens1)
        node = PrintNode(elements, opened.pos)

    elif is_front(tokens, [TokenSpecies.WHILE, TokenSpecies.IF]):
        is_while = TokenSpecies.WHILE == tokens[0].species

        _, tokens0 = get_or_riot(tokens[1:], TokenSpecies.OPENBR)
        parameters, tokens1 = parse_value(tokens0)
        _, tokens1_0 = get_or_riot(tokens1, TokenSpecies.CLOSEBR)

        instructions, tokens2 = parse_instructions(tokens1_0)
        node = IfWhileNode(parameters, instructions, is_while)
    else:
        return [], tokens

    _, tokens3 = get_or_riot(tokens2, TokenSpecies.END)
    other_nodes, tokens4 = parse_instructions(tokens3)
    return [node] + other_nodes, tokens4


# parse_params :: List[Token] -> Tuple[List[Type[ValueNode]], List[Token]]
@deepcopy_decorator
def parse_params(tokens: List[Token]) -> Tuple[List[Type[ValueNode]], List[Token]]:
    """ Parse values until an ending token is encountered. """
    val, tokens0 = parse_value(tokens)
    if is_front(tokens0, [TokenSpecies.SEP]):
        _, *tokens1 = tokens
        other_val, tokens2 = parse_params(tokens1)
        return [val] + other_val, tokens2

    _, tokens3 = get_or_riot(tokens0, TokenSpecies.CLOSEBR)
    return [val], tokens3


# parse_value :: List[Token] -> Token -> Optional[Type[ValueNode]] -> Tuple[Type[Node], List[Token]]
@deepcopy_decorator
def parse_value(tokens: List[Token], operation: Optional[Token] = None, lhs: Optional[Type[ValueNode]] = None) -> Tuple[Type[ValueNode], List[Token]]:
    """ Parse value until an ending token is encountered. """
    if is_front(tokens, [TokenSpecies.DIGIT]):
        value_token, *tokens0 = tokens
        val = IntNode(value_token)
    elif is_front(tokens, [TokenSpecies.ID]) and is_front(tokens[1:], [TokenSpecies.OPENBR]):
        name = tokens[0]
        if is_front(tokens[2:], [TokenSpecies.CLOSEBR]):
            tokens0 = tokens[3:]
            val = FuncExeNode(name, [])
        else:
            pars, tokens0 = parse_params(tokens[2:])
            val = FuncExeNode(name, pars)

    elif is_front(tokens, [TokenSpecies.ID]):
        name, *tokens0 = tokens
        val = VariableNode(name)
    else:
        raise ParserError("value, variable or function", tokens[0] if len(tokens) != 0 else None)

    val0 = OperationNode(lhs, operation, val) if lhs else val
    if is_front(tokens0, [TokenSpecies.ADD, TokenSpecies.SUB, TokenSpecies.NOTEQUAL, TokenSpecies.GREATER,
                          TokenSpecies.EQUALS, TokenSpecies.LESSER]):
        val1, tokens1 = parse_value(tokens0[1:], tokens0[0], val0)
    else:
        tokens1 = tokens0
        val1 = val0

    if is_front(tokens1, [TokenSpecies.SEP, TokenSpecies.CLOSEBR, TokenSpecies.END]):
        return val1, tokens1

    raise ParserError(TokenSpecies.END.name, tokens1[0] if len(tokens1) != 0 else None)


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content)
    print(parser(tokenized_code))

