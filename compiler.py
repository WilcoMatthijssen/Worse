from lexer import lexer
from parse import parser
from functools import reduce
from classes import *


class CompilerError(Exception):
    """ Error for when something goes wrong compiling the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


# asm_value :: ASM -> Type[ValueNode] -> str
@deepcopy_decorator
def asm_value(asm: ASM, node: Type[ValueNode]) -> str:
    """ Converts a Node to Cortex M0 Assembly. """
    if isinstance(node, IntNode):
        if 0 < int(node.value) > 255:
            raise CompilerError(f"Value {node.value} at {node.pos} can't be assigned directly")
        new = f"\tMOV R0, #{node.value}"

    elif isinstance(node, VariableNode):
        if f"{asm.curr}_{node.name}" not in asm.vars:
            raise RuntimeError(f"Variable {node.name} at {node.pos} has not been defined in {asm.curr}")
        new = f"\tLDR R2, ={asm.curr}_{node.name}\n\tLDR R0, [R2]"

    elif isinstance(node, OperationNode):

        lhs = asm_value(asm, node.lhs)
        push = "\tPUSH {R0}"
        rhs = asm_value(asm, node.rhs)
        pop = "\tPOP {R1}"

        # Get assembly to apply operation
        if node.operator == TokenSpecies.ADD:
            operation = "\tADD R0, R1, R0"
        elif node.operator == TokenSpecies.SUB:
            operation = "\tSUB R0, R1, R0"
        elif node.operator == TokenSpecies.EQUALS:
            operation = f"\tCMP R0, R1\n\tMOV R0, #1\t\nBEQ _{node.pos}_EQUALS\n\tMOV R0, #0\n_{node.pos}_EQUALS"
        elif node.operator == TokenSpecies.NOTEQUAL:
            operation = f"\tCMP R0, R1\n\tMOV R0, #1\t\nBNE _{node.pos}_NOTEQUAL\n\tMOV R0, #0\n_{node.pos}_NOTEQUAL"
        elif node.operator == TokenSpecies.LESSER:
            operation = f"\tCMP R0, R1\n\tMOV R0, #1\t\nBLT _{node.pos}_LESSER\n\tMOV R0, #0\n_{node.pos}_LESSER"
        else:  # node.operator == TokenSpecies.GREATER:
            operation = f"\tCMP R0, R1\n\tMOV R0, #1\t\nBGT _{node.pos}_GREATER\n\tMOV R0, #0\n_{node.pos}_GREATER"

        new = "\n".join([lhs, push, rhs, pop, operation])

    else:  # isinstance(node, FuncExeNode):
        # Check if function exists.
        if node.name not in asm.defs.keys():
            raise CompilerError(f"Function \"{node.name}\" not defined.")

        # Check if amount of given params is correct.
        if (name_amount := len(asm.defs[node.name].params)) != (value_amount := len(node.params)):
            raise CompilerError(f"Expected {name_amount} but got {value_amount} for function {node.name}.")

        values = map(lambda p: asm_value(asm, p), node.params)
        assign = map(lambda par_name: f"\tLDR R2, ={node.name}_{par_name}\n\tSTR R0, [R2]", asm.defs[node.name].params)
        new = "\n".join(map(lambda tup: "\n".join(tup), zip(values, assign))) + f"\n\tBL {node.name}"

    return new


# asm_action :: ASM -> Type[ActionNode] -> ASM
@deepcopy_decorator
def asm_action(asm: ASM, node: Type[ActionNode]) -> ASM:
    """ Converts an action to Cortex M0 assembly. """
    if isinstance(node, AssignNode):
        # Add variable to list of variables
        variables = asm.vars + [f"{asm.curr}_{node.name}"]

        # Get assembly for getting a value and create assembly for storing it
        value = f"{asm_value(asm, node.value)}\n\tLDR R2, ={variables[-1]}\n\tSTR R0, [R2]"

        new = ASM(asm.curr, variables, asm.defs, "\n".join([asm.body, value]))

    elif isinstance(node, IfWhileNode):
        label = f"_{node.pos}"

        # Create comparison for if/while statement
        check = f"{label}_ifwhile_condition:\n{asm_value(asm, node.condition)}\n\tCMP R0, #0\n\tBEQ {label}_ifwhile_end"

        # Get asm for actions inside while/if statement.
        tmp = ASM(asm.curr, asm.vars, asm.defs, "\n".join([asm.body, check]))
        act = reduce(asm_action, node.actions, tmp)

        # Create ending for if/while loop
        end = (f"\tB {label}_ifwhile_condition" if node.is_while else "") + f"\n{label}_ifwhile_end:"

        new = ASM(act.curr, act.vars, act.defs, act.body + end)

    else:  # isinstance(node, PrintNode):
        # Get assembly for each value and add assembly to print them.
        print_calls = "\n".join(map(lambda val_node: f"{asm_value(asm, val_node)}\n\tBL uart_put_char", node.value))

        new = ASM(asm.curr, asm.vars, asm.defs, "\n".join([asm.body, print_calls]))

    return new


# asm_function :: FuncDefNode -> Dict[str, FuncDefNode] -> Tuple[str, List[str]]
@deepcopy_decorator
def asm_function(node: FuncDefNode, functions: Dict[str, FuncDefNode]) -> Tuple[str, List[str]]:
    """ Creates a function in Cortex M0 assembly from a FuncDefNode. """
    # Create initial function ASM object
    variables = list(map(lambda param: f"{node.name}_{param}", node.params.keys()))
    start = f"{node.name}:\n\tPUSH {{R1, LR}}"

    # Get assembly for actions of function.
    asm = reduce(asm_action, node.actions, ASM(node.name, variables, functions, start))

    # Check if function returns a value.
    if f"{node.name}_sos" not in asm.vars:
        raise CompilerError(f"{node.name} at {node.pos} does not return a value.")

    # Create assembly to return value from function
    ending = f"\n\tLDR R2, ={node.name}_sos\n\tLDR R0, [R2]\n\tPOP {{ R1, PC }}\n"

    return asm.body + ending, asm.vars


# assemble :: List[FuncDefNode] -> str -> str
@deepcopy_decorator
def compiler(ast: List[FuncDefNode], start_func: str = "main") -> str:
    """ Converts a list of FuncDefNodes to Cortex M0 assembly. """
    # Make dict of List of functions with the name of the function being the key
    funcs = dict(map(lambda func: (func.name, func), ast))

    if start_func not in funcs.keys():
        raise CompilerError(f"Wanted to start at {start_func} but the function does not exist.")
    if func_len := len(funcs[start_func].params) != 0:
        raise CompilerError(f"The {start_func} function can't be given parameters but expects {func_len}.")

    # Get assembly for all functions and names for all variables
    instructions, variables = zip(*map(lambda n: asm_function(n, funcs), ast))
    flattened_variables = list(dict.fromkeys(sum(variables, [])))

    # Assemble all components to a single string of assembly code
    init = "\n".join([".cpu cortex-m0", ".align 4", ".global __main"])
    data = "\n.data\n" + "\n".join(map(lambda v: f"{v}: .word 0", flattened_variables))
    text = "\n.text\n" + "\n".join(instructions)
    base = "\n\t".join(["__main:", "PUSH { LR }", f"BL {start_func}", "POP { PC }"])
    return "\n".join([init, data, text, base])


if __name__ == "__main__":
    file = open("Worse.txt")
    file_content = file.read()
    file.close()

    tokenized_code = lexer(file_content)
    a = parser(tokenized_code)
    print(compiler(a))
