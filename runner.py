from lexer import lexer
from parse import parser
from classes import *
import operator


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


# -------------------------------------------------------------------------------------------------------------------- #
#                                            Action interpreting                                                       #
# -------------------------------------------------------------------------------------------------------------------- #


# execute_function_by_name :: str -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_function_by_name(function_name: str, parameter_values: List[int], functions: Dict[str, FuncDefNode]):
    if function_name not in functions:
        raise RunnerError(f"Function \"{function_name}\" does not exist.")

    function = functions.get(function_name)
    variables = dict(zip(function.params, parameter_values))
    for sub_action in function.actions:
        variables = execute_action(sub_action, variables, functions)

    if "sos" not in variables:
        RunnerError(f"Function {function_name} doesn't return a value.")
    return variables.get("sos")


# execute_action :: Type[ActionNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_action(action: Type[ActionNode], variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    if isinstance(action, AssignNode):
        return execute_assign(action, variables, functions)

    elif isinstance(action, PrintNode):
        return execute_print(action, variables, functions)

    elif isinstance(action, IfWhileNode):
        return execute_if_or_while(action, variables, functions)

    else:
        raise RunnerError(f"Action at {action.pos} of type {type(action)} isn't supported")


# execute_assign :: AssignNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_assign(action: AssignNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    value = retrieve_value(action.value, variables, functions)
    variables[action.name] = value
    return variables


# execute_print :: PrintNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_print(action: PrintNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    values = [retrieve_value(value_node, variables, functions) for value_node in action.value]
    values_as_char = map(chr, values)
    print(*values_as_char)
    return variables


# execute_if_or_while :: IfWhileNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_if_or_while(action: IfWhileNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    while True:
        # Prevent from running code when condition evaluates as 0.
        if retrieve_value(action.condition, variables, functions) == 0:
            break

        for sub_action in action.actions:
            variables = execute_action(sub_action, variables, functions)

        # Prevent from running multiple times when given action is not a while loop.
        if action.is_while == 0:
            break
    return variables


# -------------------------------------------------------------------------------------------------------------------- #
#                                            Value interpreting                                                        #
# -------------------------------------------------------------------------------------------------------------------- #


# retrieve_value :: Type[ValueNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def retrieve_value(action: Type[ValueNode], variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    if isinstance(action, OperationNode):
        return execute_operation(action, variables, functions)

    elif isinstance(action, VariableNode):
        return retrieve_value_from_variable(action, variables, functions)

    elif isinstance(action, IntNode):
        return retrieve_value_from_int(action, variables, functions)

    elif isinstance(action, FuncExeNode):
        return execute_function(action, variables, functions)

    else:
        raise RunnerError(f"Action at {action.pos} of type {type(action)} isn't supported")


# get_operator_by_name :: TokenSpecies -> operator
def get_operator_by_name(operator_name: TokenSpecies):
    operators = {
        TokenSpecies.ADD: operator.add,
        TokenSpecies.SUB: operator.sub,
        TokenSpecies.GREATER: operator.gt,
        TokenSpecies.LESSER: operator.lt,
        TokenSpecies.EQUALS: operator.eq,
        TokenSpecies.NOTEQUAL: operator.ne,
        TokenSpecies.MUL: operator.mul,
        TokenSpecies.DIV: operator.floordiv
    }
    if operator_name not in operators:
        raise RunnerError(f"Operator {operator_name} doesn't exist.")
    return operators[operator_name]


# execute_operation :: OperationNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_operation(action: OperationNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    lhs = retrieve_value(action.lhs, variables, functions)
    rhs = retrieve_value(action.rhs, variables, functions)
    operator_func = get_operator_by_name(action.operator)

    return int(operator_func(lhs, rhs))


# retrieve_value_from_variable :: VariableNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def retrieve_value_from_variable(action: VariableNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    if action.name not in variables:
        raise RunnerError(f"Variable {action} at {action.pos} doesn't exist.")
    return variables.get(action.name)


# retrieve_value_from_int :: IntNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def retrieve_value_from_int(action: IntNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    try:
        return int(action.value)
    except ValueError:
        raise RunnerError(f"Can't interpret {action} at {action.pos} to int.")


# execute_function :: FuncExeNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
def execute_function(action: FuncExeNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    parameters = [retrieve_value(value, variables, functions) for value in action.params]
    return execute_function_by_name(action.name, parameters, functions)


# -------------------------------------------------------------------------------------------------------------------- #
#                                            Main functions                                                            #
# -------------------------------------------------------------------------------------------------------------------- #

# runner :: List[FuncDefNode] -> str -> None
def runner(function_list: List[FuncDefNode], begin_func_name: str = "main"):
    functions = {func.name: func for func in function_list}
    print(execute_function_by_name(begin_func_name, [], functions))


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content)
    ast = parser(tokenized_code)
    runner(ast)




