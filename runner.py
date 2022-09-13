import pathlib
import operator
from typing import  List, Type, Dict
import sys
from lexer import lexer
from parse import parser
import classes as cl


sys.setrecursionlimit(1200)


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """

    def __init__(self, msg: str):
        super().__init__(msg)


# ------------------------------------------- #
#              Action interpreting            #
# ------------------------------------------- #


def execute_function_by_name(function_name: str, parameter_values: List[int], functions: Dict[str, cl.FuncDefNode]):
    """execute_function_by_name :: str -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    if function_name not in functions:
        raise RunnerError(f"Function \"{function_name}\" does not exist.")

    function = functions.get(function_name)
    variables = dict(zip(function.params, parameter_values))
    for sub_action in function.actions:
        variables = execute_action(sub_action, variables, functions)

    if "sos" not in variables:
        RunnerError(f"Function {function_name} doesn't return a value.")
    return variables.get("sos")


def dict_executor(key, dictionary, parameters, err):
    if key not in dictionary:
        raise err
    return dictionary[key](*parameters)


def execute_action(action: Type[cl.ActionNode], variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_action :: Type[ActionNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    options = {
        cl.AssignNode: execute_assign,
        cl.PrintNode: execute_print,
        cl.IfWhileNode: execute_if_or_while
    }
    err = RunnerError(
        f"Action at {action.pos} of type {type(action)} isn't supported")
    return dict_executor(type(action), options, (action, variables, functions), err)



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


# -------------------------------------------------- #
#                  Value interpreting                #
# -------------------------------------------------- #



def retrieve_value(action: Type[cl.ValueNode], variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """retrieve_value :: Type[ValueNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    options = {
        cl.OperationNode: execute_operation,
        cl.VariableNode: retrieve_value_from_variable,
        cl.IntNode: retrieve_value_from_int,
        cl.FuncExeNode: execute_function
    }
    err = RunnerError(
        f"Action at {action.pos} of type {type(action)} isn't supported")
    return dict_executor(type(action), options, (action, variables, functions), err)


def execute_operation(action: cl.OperationNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_operation :: OperationNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    lhs = retrieve_value(action.lhs, variables, functions)
    rhs = retrieve_value(action.rhs, variables, functions)
    operators = {
        cl.TokenSpecies.ADD: operator.add,
        cl.TokenSpecies.SUB: operator.sub,
        cl.TokenSpecies.GREATER: operator.gt,
        cl.TokenSpecies.LESSER: operator.lt,
        cl.TokenSpecies.EQUALS: operator.eq,
        cl.TokenSpecies.NOTEQUAL: operator.ne,
        cl.TokenSpecies.MUL: operator.mul,
        cl.TokenSpecies.DIV: operator.floordiv
    }
    match action.operator:
        case cl.TokenSpecies.ADD:
            oper = operator.add
        case cl.TokenSpecies.SUB:
            oper = operator.sub
        case cl.TokenSpecies.GREATER:
            oper = operator.gt
        case cl.TokenSpecies.LESSER:
            oper = operator.lt
        case cl.TokenSpecies.EQUALS:
            oper = operator.eq
        case cl.TokenSpecies.NOTEQUAL:
            oper = operator.ne
        case cl.TokenSpecies.MUL:
            oper = operator.mul
        case cl.TokenSpecies.DIV:
            oper = operator.floordiv
        case _:
            raise RunnerError(f"Operator {action.operator} doesn't exist.")
    return int(oper(lhs, rhs))


def retrieve_value_from_variable(action: cl.VariableNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """retrieve_value_from_variable :: VariableNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    if action.name not in variables:
        raise RunnerError(f"Variable {action} at {action.pos} doesn't exist.")
    return variables.get(action.name)


def retrieve_value_from_int(action: cl.IntNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """retrieve_value_from_int :: IntNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    try:
        return int(action.value)
    except ValueError:
        raise RunnerError(f"Can't interpret {action} at {action.pos} to int.")


def execute_function(action: cl.FuncExeNode, variables: Dict[str, int], functions: Dict[str, cl.FuncDefNode]):
    """execute_function :: FuncExeNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int"""
    parameters = [retrieve_value(value, variables, functions)
                  for value in action.params]
    return execute_function_by_name(action.name, parameters, functions)


# --------------------------------------------- #
#              Main functions                   #
# --------------------------------------------- #
def runner(function_list: List[cl.FuncDefNode], begin_func_name: str = "main"):
    """runner :: List[FuncDefNode] -> str -> None"""
    functions = {func.name: func for func in function_list}
    print(execute_function_by_name(begin_func_name, [], functions))


if __name__ == "__main__":
    file_content = pathlib.Path("Worse.txt").read_text("utf-8")
    tokenized_code = lexer(file_content)
    ast = parser(list(tokenized_code))
    runner(ast)
