import pathlib
import operator
from typing import  List, Type, Dict
import sys
from lexer import lexer
from parse import parser
import classes as cl
sys.setrecursionlimit(700)


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """


def execute_function_by_name(name: str, parameters: List[int], functions: Dict[str, cl.FuncDefNode]):
    """execute_function_by_name :: str -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    if name not in functions:
        raise RunnerError(f"Function \"{name}\" does not exist.")

    function = functions.get(name)
    variables = dict(zip(function.params, parameters))
    for sub_action in function.actions:
        variables = execute_action(sub_action, variables, functions)

    if "sos" not in variables:
        RunnerError(f"Function {name} doesn't return a value.")
    return variables.get("sos")


def execute_action(action: cl.ActionNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_action :: Type[ActionNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    match action:
        case cl.AssignNode():
            return execute_assign(action, variables, functions)
        case cl.PrintNode():
            return execute_print(action, variables, functions)
        case cl.IfWhileNode():
            return execute_if_or_while(action, variables, functions)
        case _:
            RunnerError(f"Action at {action.pos} of type {type(action)} isn't supported")
    return None # Can't reach this but Pylint will go crazy without


def execute_assign(action: cl.AssignNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_assign :: AssignNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    variables[action.name] = retrieve_value(action.value, variables, functions)
    return variables


def execute_print(action: cl.PrintNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_print :: PrintNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    values_as_char = map(
        lambda val: chr(retrieve_value(val, variables, functions)),
        action.value)
    print(*values_as_char)
    return variables


def execute_if_or_while(action: cl.IfWhileNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_if_or_while :: IfWhileNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    while retrieve_value(action.condition, variables, functions) != 0:
        for sub_action in action.actions:
            variables = execute_action(sub_action, variables, functions)
        if action.is_while == 0:
            break
    return variables


def retrieve_value(action: cl.ValueNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]) -> int:
    """retrieve_value :: Type[ValueNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    match action:
        case cl.OperationNode():
            return execute_operation(action, variables, functions)
        case cl.VariableNode():
            if action.name in variables:
                return variables.get(action.name)
            raise RunnerError(f"Variable {action} at {action.pos} doesn't exist.")
        case cl.IntNode():
            return int(action.value)
        case cl.FuncExeNode():
            parameters = (retrieve_value(value, variables, functions) for value in action.params)
            return execute_function_by_name(action.name, parameters, functions)
        case _:
            raise RunnerError(f"Action at {action.pos} of type {type(action)} isn't supported")
    return None # Can't reach this but Pylint will go crazy without

def execute_operation(action: cl.OperationNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_operation :: OperationNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    lhs = retrieve_value(action.lhs, variables, functions)
    rhs = retrieve_value(action.rhs, variables, functions)
    match action.operator:
        case cl.TokenSpecies.ADD:
            return operator.add(lhs, rhs)
        case cl.TokenSpecies.SUB:
            return operator.sub(lhs, rhs)
        case cl.TokenSpecies.GREATER:
            return operator.gt(lhs, rhs)
        case cl.TokenSpecies.LESSER:
            return operator.lt(lhs, rhs)
        case cl.TokenSpecies.EQUALS:
            return operator.eq(lhs, rhs)
        case cl.TokenSpecies.NOTEQUAL:
            return operator.ne(lhs, rhs)
        case cl.TokenSpecies.MUL:
            operator.mul(lhs, rhs)
        case cl.TokenSpecies.DIV:
            return operator.floordiv(lhs, rhs)
        case _:
            raise RunnerError(f"Operator {action.operator} doesn't exist.")
    return None # Can't reach this but Pylint will go crazy without

def runner(function_list: List[cl.FuncDefNode], begin_func_name: str = "main"):
    """runner :: List[FuncDefNode] -> str -> None"""
    functions = {func.name: func for func in function_list}
    print(execute_function_by_name(begin_func_name, [], functions))


if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text("utf-8")
    tokenized_code = lexer(file_content)
    ast = parser(list(tokenized_code))
    runner(ast)
