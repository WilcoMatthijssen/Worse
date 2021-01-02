from lexer import lexer
from parse import parser
from classes import *
import operator
from functools import reduce
import sys
sys.setrecursionlimit(10000)


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


# get_op_func :: Type[Enum] -> Callable
@deepcopy_decorator
def get_op_func(species: Type[Enum]) -> Callable:
    """ Give corresponding function to enum"""
    op = {TokenSpecies.ADD: operator.add,
          TokenSpecies.SUB: operator.sub,
          TokenSpecies.GREATER: operator.gt,
          TokenSpecies.LESSER: operator.lt,
          TokenSpecies.EQUALS: operator.eq,
          TokenSpecies.NOTEQUAL: operator.ne,
          TokenSpecies.MUL: operator.mul,
          TokenSpecies.DIV: operator.floordiv}
    return op[species]


# get_value :: Type[ValueNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
@deepcopy_decorator
def get_value(action: Type[ValueNode], variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> int:
    """ Gets integer value of given action. """
    value = 0
    if isinstance(action, OperationNode):
        lhs = get_value(action.lhs, variables, functions)
        rhs = get_value(action.rhs, variables, functions)
        value = int(get_op_func(action.operator)(lhs, rhs))

    elif isinstance(action, VariableNode):
        if action.name not in variables.keys():
            raise RunnerError(f"Variable \"{action.name}\" at character {action.pos} not defined.")
        value = variables[action.name]

    elif isinstance(action, IntNode):
        value = int(action.value)

    elif isinstance(action, FuncExeNode):
        if action.name not in functions.keys():
            raise RunnerError(f"Function \"{action.name}\" at character {action.pos} does not exist.")
        param_values = list(map(lambda val: get_value(val, variables, functions), action.params))
        if len(param_values) != len(functions[action.name].params.keys()):
            raise RunnerError(f"Params for \"{action.name}\" given at character {action.pos} dont match function.")

        parameters = dict(zip(functions[action.name].params.keys(), param_values))
        value = run_function(action.name, parameters, functions)

    return value


# run_ifwhile :: IfWhileNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> Dict[str, int]
@deepcopy_decorator
def run_ifwhile(loop: IfWhileNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> Dict[str, int]:
    """ Run if or while loop recursively. """
    if get_value(loop.condition, variables, functions) != 0:
        new_vars = reduce(lambda var, action: run_action(var, functions, action), loop.actions, variables)
        if loop.is_while:
            return run_ifwhile(loop, new_vars, functions)
        return new_vars
    return variables


# run_action :: Dict[str, int] -> Dict[str, FuncDefNode] -> Type[ActionNode] -> Dict[str, int]
@deepcopy_decorator
def run_action(var: Dict[str, int], funcs: Dict[str, FuncDefNode], action: Type[ActionNode]) -> Dict[str, int]:
    """ Runs action and returns updated variables and unchanged functions for the use of reduce. """

    if isinstance(action, AssignNode):
        new_vars = {**var, **{action.name: get_value(action.value, var, funcs)}}
    elif isinstance(action, PrintNode):
        print("".join(map(lambda val: chr(get_value(val, var, funcs)), action.value)))
        new_vars = var
    else:  # isinstance(action, IfWhileNode):
        new_vars = run_ifwhile(action, var, funcs)
    return new_vars


# run_function ::  str -> Dict[str, int] ->  Dict[str, FuncDefNode] -> int
@deepcopy_decorator
def run_function(func_name: str, variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> int:
    """ Execute function and return the "sos" variable. """
    # Check is func exists.
    if func_name not in functions.keys():
        raise RunnerError(f"Function \"{func_name}\" not defined")

    # Run function
    new_vars = reduce(lambda var, action: run_action(var, functions, action), functions[func_name].actions, variables)

    # Check if function returns value.
    if "sos" in new_vars.keys():
        return new_vars["sos"]
    raise RunnerError(f"Function \"{func_name}\" at character {functions[func_name].pos} doesn't assign a value to sos")


# runner ::  List[FuncDefNode] -> str -> None
@deepcopy_decorator
def runner(ast: List[FuncDefNode], start_func_name: str = "main") -> None:
    """ Runs the ast by executing the start_func_name. """

    functions = dict(map(lambda func: (func.name, func), ast))
    print(f"Process starting with function: {start_func_name}")
    result = run_function(start_func_name, {}, functions)
    print(f"Process finished with {result}")
    return result



if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content)
    ast = parser(tokenized_code)
    runner(ast)




