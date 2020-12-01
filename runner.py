from lexer import *
from parse import *
from copy import deepcopy
import operator
import gui


class RunnerError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def retrieve_multi_value(values, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    return list(map(lambda val: retrieve_single_value(val, variables, functions), values))


def retrieve_single_value(action: Union[OperationNode, VariableNode, ValueNode, FuncExeNode], variables: Dict[str, int],
                          functions: Dict[str, FuncDefNode]) -> int:
    op = {TokenSpecies.ADD:         operator.add,
          TokenSpecies.SUB:         operator.sub,
          TokenSpecies.GREATER:     operator.gt,
          TokenSpecies.LESSER:      operator.lt,
          TokenSpecies.EQUALS:      operator.eq,
          TokenSpecies.NOTEQUAL:    operator.ne}

    val = 0
    if action.__class__.__name__ == "OperationNode":
        a = retrieve_single_value(action.lhs, variables, functions)
        b = retrieve_single_value(action.rhs, variables, functions)
        val = op[action.operator](a, b)

    elif action.__class__.__name__ == "VariableNode":
        if action.name in variables.keys():
            val = variables[action.name]
        else:
            raise RunnerError(f"VariableNode {action.name} at ... has not been declared.")

    elif action.__class__.__name__ == "ValueNode":
        val = int(action.value)

    elif action.__class__.__name__ == "FuncExeNode":
        fl = retrieve_multi_value(action.params, variables, functions)
        assert len(fl) == len(functions[action.name].params.keys())
        fp = dict(zip(functions[action.name].params.keys(), fl))
        val = run_function(functions[action.name].code, fp, functions)

    return val


def run_print(values, variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> None:
    vals = retrieve_multi_value(values, variables, functions)
    message = "".join(map(lambda integer: chr(integer), vals))

    gui.gui_print(message)
    print(message)


def run_ifwhile(actions, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    if retrieve_single_value(actions.expression, variables, functions) != 0:
        variables = run_actions(actions.code, variables, functions)
        if actions.is_while:
            variables = run_ifwhile(actions, variables, functions)

    return variables


def run_actions(actions, variables: Dict[str, int], functions: Dict[str, FuncDefNode]):
    instructions = deepcopy(actions)
    if len(instructions) == 0:
        return variables

    stuff: Union[AssignNode, PrintNode, IfWhileNode] = instructions.pop(0)
    if stuff.__class__.__name__ == "AssignNode":
        variables[stuff.name] = retrieve_single_value(stuff.value, variables, functions)
    elif stuff.__class__.__name__ == "PrintNode":
        run_print(stuff.value, variables, functions)
    elif stuff.__class__.__name__ == "IfWhileNode":
        variables = run_ifwhile(stuff, variables, functions)

    return run_actions(instructions, variables, functions)


def run_function(instructions: List[Union[AssignNode, PrintNode, IfWhileNode]],
                 variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> int:
    variables = run_actions(instructions, variables, functions)
    return variables["sos"] if "sos" in variables.keys() else 0


def runner(ast: List[FuncDefNode], start_func_name: str):
    functions = dict(map(lambda func: (func.name, func), ast))
    result= run_function(functions[start_func_name].code, functions[start_func_name].params, functions)

    gui.gui_print(f"Process finished with {result}")
    return result

if __name__ == '__main__':
    gui.main()




