from lexer import *
from parse import *
from functools import reduce
from typing import Dict
from copy import deepcopy as dc

class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


class ASM:
    def __init__(self, curr_func: str, variables: List[str], func_defs: Dict[str, FuncDefNode], asm_items: str):
        self.curr_func = curr_func
        self.variables = variables
        self.func_defs = func_defs
        self.asm_items = asm_items

# asm_value :: ASM -> Union[ValueNode, VariableNode, OperationNode, FuncExeNode] -> str
def asm_value(asm: ASM, node: Union[ValueNode, VariableNode, OperationNode, FuncExeNode]) -> str:
    if isinstance(node, ValueNode):
        if 0 < int(node.value) > 255:
            raise RunnerError(f"Value {node.value} at {node.pos} can't be assigned directly")
        asm_text = f"\tMOV R0, #{node.value}"

    elif isinstance(node, VariableNode):
        if f"{asm.curr_func}_{node.name}" not in asm.variables:
            raise RuntimeError(f"Variable {node.name} tried to be read at {node.pos} but has not been defined in {asm.curr_func}")
        asm_text = f"\tLDR R2, ={asm.curr_func}_{node.name}\n\tLDR R0, [R2]"

    elif isinstance(node, OperationNode):
        lhs = asm_value(asm, node.lhs)
        push = "\tPUSH {R0}"
        rhs = asm_value(asm, node.rhs)
        pop = "\tPOP {R1}"
        if node.operator == TokenSpecies.ADD:
            operation = "\tADD R0, R1, R0"
        elif node.operator == TokenSpecies.SUB:
            operation = "\tSUB R0, R1, R0"
        else:
            raise AssertionError("OPERATION")
        asm_text = "\n".join([lhs, push, rhs, pop, operation])

    else:  # node.__class__.__name__ == "FuncExeNode"
        # Check if function exists.
        if node.name not in asm.func_defs.keys():
            raise RunnerError(f"Function \"{node.name}\" not defined.")

        # Check if amount of given params is correct.
        if (name_amount := len(asm.func_defs[node.name].params)) != (value_amount := len(node.params)):
            raise RunnerError(f"Expected {name_amount} but got {value_amount} for function {node.name}.")

        # Create assembly to give values to parameters for function call.
        # p_values = map(lambda param_node: asm_value(asm, param_node), node.params)
        # p_names = map(lambda name: f"{node.name}_{name}", asm.func_defs[node.name].params)
        # parameter_asm = map(lambda name, val: f"{val}\n\tLDR R2, ={name}\n\tSTR R0, [R2]", zip(p_names, p_values))
        # #print(node.params)
        # #print(list(p_values))
        # # Create assembly to call function.
        # function_call = f"\n\tBL {node.name}"
        # #print(list(parameter_asm))
        #asm_text = "\n".join(parameter_asm) + function_call
        values = map(lambda p: asm_value(asm, p), node.params)
        assignments = map(lambda param_name: f"\tLDR R2, ={node.name}_{param_name}\n\tSTR R0, [R2]",
                          asm.func_defs[node.name].params)
        function_parameters = list(map(lambda tup: "\n".join(tup), zip(values, assignments)))

        function_call = f"\tBL {node.name}"
        asm_text = "\n".join(function_parameters + [function_call])

    return asm_text


# asm_action :: ASM -> Union[AssignNode, IfWhileNode, PrintNode] -> ASM
def asm_action(asm: ASM, node: Union[AssignNode, IfWhileNode, PrintNode]) -> ASM:
    if isinstance(node, AssignNode):
        # Add variable to list of variables
        variables = asm.variables + [f"{asm.curr_func}_{node.name}"]

        # Get assembly for getting a value and create assembly for storing it
        value = asm_value(asm, node.value)
        load_ = f"\tLDR R2, ={variables[-1]}"
        store = f"\tSTR R0, [R2]"
        new_assembly = "\n".join([asm.asm_items, value, load_, store])

        new_asm = ASM(asm.curr_func, variables, asm.func_defs, new_assembly)

    elif isinstance(node, IfWhileNode):
        label = f"_{len(asm.asm_items)}{asm.curr_func}"

        # Create comparison for while/if statement
        start = f"{label}_ifwhile_conditional:"
        value = asm_value(asm, node.condition)
        check = f"\tCMP R0, #0"
        final = f"\tBEQ {label}_ifwhile_end"
        new_assembly = "\n".join([asm.asm_items, start, value, check, final])

        # Get asm for actions inside while/if statement.
        tmp_asm = ASM(asm.curr_func, asm.variables, asm.func_defs, new_assembly)
        act_asm = reduce(asm_action, node.actions, tmp_asm)

        # Create ending for while/if loop

        end = (f"\tB {label}_ifwhile_conditional" if node.is_while else "") + f"\n{label}_ifwhile_end:"

        # Remove duplicate variables
        var = list(dict.fromkeys(act_asm.variables + asm.variables))

        new_asm = ASM(asm.curr_func, var, asm.func_defs, act_asm.asm_items + end)

    else:  # isinstance(node, PrintNode):
        # Get assembly for each value and add assembly to print them.
        print_calls = "\n".join(map(lambda val_node: f"{asm_value(asm, val_node)}\n\tBL uart_to_char", node.value))

        new_asm = ASM(asm.curr_func, asm.variables, asm.func_defs, "\n".join([asm.asm_items, print_calls]))

    return new_asm


# asm_function :: FuncDefNode -> Dict[str, FuncDefNode] -> Tuple[str, List[str]]
def asm_function(node: FuncDefNode, functions: Dict[str, FuncDefNode]) -> Tuple[str, List[str]]:
    # Create initial function ASM object
    variables = list(map(lambda param: f"{node.name}_{param}", node.params.keys()))
    start_asm = f"{node.name}:\n\tPUSH {{R1, LR}}"

    # Get assembly for actions of function.
    new_asm = reduce(asm_action, node.actions, ASM(node.name, variables, functions, start_asm))

    # Check if function returns a value.
    if f"{node.name}_sos" not in new_asm.variables:
        raise RunnerError(f"{node.name} does not return a value.")

    # Create assembly to return value from function
    return_asm = f"\n\tLDR R2, ={node.name}_sos\n\tLDR R0, [R2]\n\tPOP {{ R1, PC }}\n"

    return new_asm.asm_items + return_asm, new_asm.variables


# assemble :: List[FuncDefNode] -> str -> str
def assemble(ast: List[FuncDefNode], start_func: str = "main") -> str:
    funcs = dict(map(lambda func: (func.name, func), ast))

    if start_func not in funcs.keys():
        raise RunnerError(f"Wanted to start at {start_func} but the function does not exist.")
    if len(funcs[start_func].params) != 0:
        raise RunnerError(f"The {start_func} function can't be given parameters but expects {len(funcs[start_func].params)}.")

    instructions, variables = zip(*map(lambda n: asm_function(n, funcs), ast))

    init = "\n".join([".cpu cortex-m0", ".align 4", ".global __main"])
    data = "\n.data\n" + "\n".join(map(lambda v: v + ": .word 0", sum(variables, [])))
    text = "\n.text\n" + "\n".join(instructions)
    base = "\n\t".join(["__main:", "PUSH { LR }", f"BL {start_func}", "POP { PC }"])
    return "\n".join([init, data, text, base])



if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
    a= parser(tokenized_code)
    print(assemble(a))
