from lexer import *
from parse import *
from copy import deepcopy
import operator

def multival(values, variables, functions):
    return list(map(lambda val: retrieve_val(val, variables, functions), values))

def retrieve_val(action, variables, functions) -> int:
    op = {TokenSpecies.ADD:         operator.add,
          TokenSpecies.SUB:         operator.sub,
          TokenSpecies.GREATER:     operator.gt,
          TokenSpecies.LESSER:      operator.lt,
          TokenSpecies.EQUALS:      operator.eq,
          TokenSpecies.NOTEQUAL:    operator.ne}

    val = 0
    if action.__class__.__name__ == "Operation":
        a = retrieve_val(action.lhs, variables, functions)
        b = retrieve_val(action.rhs, variables, functions)
        val = op[action.operator](a, b)

    elif action.__class__.__name__ == "Variable":
        val = variables[action.name] if action.name in variables.keys() else 0

    elif action.__class__.__name__ == "Value":
        val = int(action.value)

    elif action.__class__.__name__ == "FuncExe":
        fl = multival(action.params, variables, functions)
        assert len(fl) == len(functions[action.name].params.keys())
        fp = dict(zip(functions[action.name].params.keys(), fl))
        val = execute_func(functions[action.name].code, fp, functions)

    return val


def printor(values, variables, functions) -> None:
    vals = multival(values, variables, functions)
    print("".join(map(lambda integer: chr(integer), vals)))
    #print(*vals)



def execute_ifwhile(action, variables, functions):
    if retrieve_val(action.expression, variables, functions) != 0:
        variables = ex(action.code, variables, functions)
        if action.is_while:
            variables = execute_ifwhile(action, variables, functions)

    return variables


#: List[Union[Assign, Print, IfWhile]]
def ex(ins, variables, functions):
    instructions = deepcopy(ins)
    if len(instructions) == 0:
        return variables

    stuff: Union[Assign, Print, IfWhile] = instructions.pop(0)
    if stuff.__class__.__name__ == "Assign":
        variables[stuff.name] = retrieve_val(stuff.value, variables, functions)
    elif stuff.__class__.__name__ == "Print":
        printor(stuff.value, variables, functions)
    elif stuff.__class__.__name__ == "IfWhile":
        variables = execute_ifwhile(stuff, variables, functions)

    return ex(instructions, variables, functions)


def execute_func(instructions: List[Union[Assign, Print, IfWhile]],
                 variables: Dict[str, int], functions) -> int:
    variables = ex(instructions, variables, functions)
    return variables["sos"] if "sos" in variables.keys() else 0


def runner(ast):
    functions = dict(map(lambda func: (func.name, func), ast))
    return execute_func(functions["main"].code, functions["main"].params, functions)


if __name__ == "__main__":
    file = open("Worse.txt")
    filecontent = file.read()
    file.close()

    tok = lexer(filecontent, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    try:
        ast = parser(tok)
        print(runner(ast))
    except ParserError as e:
        print(e)
