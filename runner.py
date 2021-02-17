from lexer import lexer
from parse import parser
from classes import *
import operator


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


def execute_function_by_name(function_name, parameter_values, functions):
    assert function_name in functions, f"Function \"{function_name}\" does not exist."

    function = functions.get(function_name)
    variables = dict(zip(function.params, parameter_values))
    for sub_action in function.actions:
        variables = execute_action(sub_action, variables, functions)

    if "sos" not in variables:
        RunnerError(f"Function {function_name} doesn't return a value.")
    return variables.get("sos")


def execute_action(action, variables, functions):
    if isinstance(action, AssignNode):
        return execute_assign(action, variables, functions)

    elif isinstance(action, PrintNode):
        return execute_print(action, variables, functions)

    elif isinstance(action, IfWhileNode):
        return execute_if_or_while(action, variables, functions)

    else:
        raise RunnerError(f"Action at {action.pos} of type {type(action)} isn't supported")


def execute_assign(action, variables, functions):
    value = retrieve_value(action.value, variables, functions)
    variables[action.name] = value
    return variables


def execute_print(action, variables, functions):
    values = [retrieve_value(value_node, variables, functions) for value_node in action.value]
    values_as_char = map(chr, values)
    print(*values_as_char)
    return variables


def execute_if_or_while(action, variables, functions):
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


def retrieve_value(action, variables, functions):
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


def get_operator_by_name(operator_name):
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
        RunnerError(f"Operator {operator_name} doesn't exist.")
    return operators[operator_name]


def execute_operation(action, variables, functions):
    lhs = retrieve_value(action.lhs, variables, functions)
    rhs = retrieve_value(action.rhs, variables, functions)
    operator_func = get_operator_by_name(action.operator)

    return int(operator_func(lhs, rhs))


def retrieve_value_from_variable(action, variables, functions):
    if action.name not in variables:
        raise RunnerError(f"Variable {action} at {action.pos} doesn't exist.")
    return variables.get(action.name)


def retrieve_value_from_int(action, variables, functions):
    try:
        return int(action.value)
    except ValueError:
        print("Can't convert value to int.")


def execute_function(action, variables, functions):
    parameters = [retrieve_value(value, variables, functions) for value in action.params]
    return execute_function_by_name(action.name, parameters, functions)


def runner(function_list, begin_func_name="main"):
    functions = {func.name: func for func in function_list}
    print(execute_function_by_name(begin_func_name, (), functions))


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content)
    ast = parser(tokenized_code)
    runner(ast, "main")




