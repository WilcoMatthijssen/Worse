from dataclasses import dataclass
from enum import Enum
from typing import List, Type, Dict


class TokenSpecies(Enum):
    WHILE   = "(?<!\w)while(?!\w)"
    IF      = "(?<!\w)if(?!\w)"
    PRINT   = "(?<!\w)print(?!\w)"
    ASSIGN  = "(?<![=:])\=(?![=:])"
    DEF     = "\?"
    END     = "\;"
    SEP     = "\,"
    EQUALS  = "\=\="
    NOTEQUAL= "\!\="
    GREATER = "\:\="
    LESSER  = "\=\:"
    ADD     = "(?<!\+)\+(?!\+)"
    MUL     = "\+\+"
    SUB     = "(?<!\-)\-(?!\-)"
    DIV     = "\-\-"
    OPENBR  = "\("
    CLOSEBR = "\)"
    ID      = "[a-zA-Z]\w*"
    DIGIT   = "[0-9]+"


@dataclass(frozen=True)
class Token:
    species: TokenSpecies
    content: str
    pos: int

    def __str__(self) -> str:
        """ returns content, pos and kind of Token. """
        return self.__repr__()

    def __repr__(self) -> str:
        """ returns content, pos and kind of Token. """
        return f"(\"{self.content}\", {self.pos}, {self.species})"


class Node:
    """ Base class for nodes. """

    def __init__(self, pos: int):
        """ Init for Node. """
        self.pos = pos

    def __str__(self) -> str:
        return f"Empty base Node at {self.pos}"

    def __repr__(self) -> str:
        return self.__str__()


class ValueNode(Node):
    """ Nodes that can return values. """
    def __init__(self, pos: int):
        """ Init for Node. """
        Node.__init__(self, pos)

    def __str__(self) -> str:
        return f"Empty value Node at {self.pos}"


class IntNode(ValueNode):
    def __init__(self, value: Token):
        """ Init for IntNode. """
        ValueNode.__init__(self, value.pos)
        self.value = value.content

    def __str__(self) -> str:
        return f"{self.value}"


class VariableNode(ValueNode):
    def __init__(self, name: Token):
        """ Init for VariableNode. """
        ValueNode.__init__(self, name.pos)
        self.name = name.content

    def __str__(self) -> str:
        return f"{self.name}"


class FuncExeNode(ValueNode):
    def __init__(self, name: Token, params: List[Type[Node]]):
        """ Init for FuncExeNode. """
        ValueNode.__init__(self, name.pos)
        self.name = name.content
        self.params = params

    def __str__(self) -> str:
        return f"{self.name} {self.params}"


class OperationNode(ValueNode):
    """ Init for operationNode. """

    def __init__(self, lhs: Type[ValueNode], operator: Token, rhs: Type[ValueNode]):
        ValueNode.__init__(self, operator.pos)
        self.operator = operator.species
        self.rhs = rhs
        self.lhs = lhs

    def __str__(self) -> str:
        return f"({self.lhs} {self.operator} {self.rhs})"


class ActionNode(Node):
    """ Nodes that do an action. """
    def __init__(self, pos: int):
        """ Init for Node. """
        Node.__init__(self, pos)

    def __str__(self) -> str:
        return f"Empty action Node at {self.pos}"


class AssignNode(ActionNode):
    def __init__(self, variable: Token, value: Type[ValueNode]):
        """ Init for AssignNode. """
        ActionNode.__init__(self, variable.pos)
        self.name = variable.content
        self.value = value

    def __str__(self) -> str:
        return f"{self.name} = {self.value}"


class PrintNode(ActionNode):
    def __init__(self, value: List[Type[ValueNode]], pos: int):
        """ Init for PrintNode. """
        ActionNode.__init__(self, pos)
        self.value = value

    def __str__(self) -> str:
        return f"print {self.value}"


class IfWhileNode(ActionNode):
    def __init__(self, condition: Type[ValueNode], actions: List[Type[ActionNode]], is_while: bool):
        """ Init for IfWhileNode. """
        ActionNode.__init__(self, condition.pos)
        self.condition = condition
        self.actions = actions
        self.is_while = is_while

    def __str__(self) -> str:
        loop = "while" if self.is_while else "if"
        return f"({loop}({self.condition}) {self.actions})"


class FuncDefNode(Node):
    def __init__(self, name: Token, params: Dict[str, int], actions: List[Type[ActionNode]]):
        """ Init for FuncDefNode. """
        Node.__init__(self, name.pos)
        self.name = name.content
        self.params = params
        self.actions = actions

    def __str__(self) -> str:
        return f"Define {self.name}({self.params}){self.actions};"


