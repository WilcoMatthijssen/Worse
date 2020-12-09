from lexer import *
from parse import *
import operator
import tkinter as tk
from tkinter import scrolledtext
import inspect
import sys
from typing import Callable
sys.setrecursionlimit(10000)


class RunnerError(Exception):
    """ Error for when something goes wrong running the Worse code """
    def __init__(self, msg: str):
        super().__init__(msg)


# logging_decorator :: Callable -> Callable
def logging_decorator(func: Callable) -> Callable:
    """ Decorator for printing function name and how far it is on the stack """
    def decorator(*args, **kwargs):
        print(f"{func.__name__}: {len(inspect.stack(0))}")
        return func(*args, **kwargs)
    return decorator


# get_op_func :: Type[Enum] -> Callable
@logging_decorator
def get_op_func(species: Type[Enum]) -> Callable:
    """ Give corresponding function to enum"""
    op = {TokenSpecies.ADD: operator.add,
          TokenSpecies.SUB: operator.sub,
          TokenSpecies.GREATER: operator.gt,
          TokenSpecies.LESSER: operator.lt,
          TokenSpecies.EQUALS: operator.eq,
          TokenSpecies.NOTEQUAL: operator.ne}
    return op[species]

# get_value :: Union[OperationNode, VariableNode, ValueNode, FuncExeNode] -> Dict[str, int] -> Dict[str, FuncDefNode] -> int
@logging_decorator
def get_value(action: Union[OperationNode, VariableNode, ValueNode, FuncExeNode], variables: Dict[str, int],
              functions: Dict[str, FuncDefNode]) -> int:
    """ Gets integer value of given action. """
    value = 0
    if action.__class__.__name__ == "OperationNode":
        lhs = get_value(action.lhs, variables, functions)
        rhs = get_value(action.rhs, variables, functions)
        value = int(get_op_func(action.operator)(lhs, rhs))

    elif action.__class__.__name__ == "VariableNode":
        if action.name not in variables.keys():
            raise RunnerError(f"Variable \"{action.name}\" at character {action.pos} not defined.")
        value = variables[action.name]

    elif action.__class__.__name__ == "ValueNode":
        value = int(action.value)

    elif action.__class__.__name__ == "FuncExeNode":
        if action.name not in functions.keys():
            raise RunnerError(f"Function \"{action.name}\" at character {action.pos} does not exist.")
        param_values = list(map(lambda val: get_value(val, variables, functions), action.params))
        if len(param_values) != len(functions[action.name].params.keys()):
            raise RunnerError(f"Params for \"{action.name}\" given at character {action.pos} dont match function.")

        parameters = dict(zip(functions[action.name].params.keys(), param_values))
        value = run_function(action.name, parameters, functions)

    return value


# run_ifwhile :: IfWhileNode -> Dict[str, int] -> Dict[str, FuncDefNode] -> Dict[str, int]
@logging_decorator
def run_ifwhile(loop: IfWhileNode, variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> Dict[str, int]:
    """ Run if or while loop recursively. """
    if get_value(loop.condition, variables, functions) != 0:
        variables, _ = reduce(run_action, loop.actions, (variables, functions))
        if loop.is_while:
            variables = run_ifwhile(loop, variables, functions)
    return variables


# run_action :: Tuple[Dict[str, int], Dict[str, FuncDefNode]] -> Union[AssignNode, PrintNode, IfWhileNode] -> Tuple[Dict[str, int], Dict[str, FuncDefNode]]
@logging_decorator
def run_action(var_fun: Tuple[Dict[str, int], Dict[str, FuncDefNode]], action: Union[AssignNode, PrintNode, IfWhileNode]) -> Tuple[Dict[str, int], Dict[str, FuncDefNode]]:
    """ Runs action and returns updated variables and unchanged functions for the use of reduce. """
    variables, functions = var_fun
    if action.__class__.__name__ == "AssignNode":
        variables[action.name] = get_value(action.value, variables, functions)
    elif action.__class__.__name__ == "PrintNode":
        printable_values = map(lambda val: get_value(val, variables, functions), action.value)
        printable_string = reduce(lambda string, val: string + chr(val), printable_values, "")
        gui_print(printable_string)
    elif action.__class__.__name__ == "IfWhileNode":
        variables = run_ifwhile(action, variables, functions)
    return variables, functions


# run_function ::  str -> Dict[str, int] ->  Dict[str, FuncDefNode] -> int
@logging_decorator
def run_function(func_name: str, variables: Dict[str, int], functions: Dict[str, FuncDefNode]) -> int:
    """ Execute function and return the "sos" variable. """
    if func_name not in functions.keys():
        raise RunnerError(f"Function \"{func_name}\" not defined")
    instructions = functions[func_name].actions
    variables, _ = reduce(run_action, instructions, (variables, functions))
    if "sos" in variables.keys():
        return variables["sos"]
    raise RunnerError(f"Function \"{func_name}\" at character {functions[func_name].pos} doesn't assign a value to sos")


# runner ::  List[FuncDefNode] -> str -> None
@logging_decorator
def runner(ast: List[FuncDefNode], start_func_name: str) -> None:
    """ Runs the ast by executing the start_func_name. """

    functions = dict(map(lambda func: (func.name, func), ast))
    gui_print(f"Process starting with function: {start_func_name}")
    result = run_function(start_func_name, {}, functions)
    gui_print(f"Process finished with {result}\n")


# worse :: str -> bool -> None
@logging_decorator
def worse(text: str, is_morse: bool = False) -> None:
    """ Interprets text as Worse code. """
    try:
        text = morse_converter(text) if is_morse else text
        tokens = lexer(text, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")
        ast = parser(tokens)
        runner(ast, "main")

    except LexerError as e:
        gui_print(f"Failed lexing because: {e}")

    except ParserError as e:
        gui_print(f"Failed parsing because: {e}")

    except RunnerError as e:
        gui_print(f"Failed running because: {e}")

    except RecursionError:
        gui_print("Maximum recursion depth exceeded")


# gui_print :: str -> None
@logging_decorator
def gui_print(text: str) -> None:
    """ Prints text to the output box on the GUI. """
    outputbox.configure(state="normal")
    outputbox.insert(tk.END, text + "\n")
    outputbox.configure(state="disabled")
    outputbox.update()
    print(text)


# switch_input :: None
@logging_decorator
def switch_input() -> None:
    """ Switches input from text to morse and back. """
    new_input = morse_converter(inputbox.get('1.0', 'end-1c'), not morse_state.get())
    inputbox.delete("1.0", tk.END)
    inputbox.insert(tk.INSERT, new_input)


# Window setup
window = tk.Tk()
window.title("Worse IDE")
window.geometry("900x800")
fixed_frame = tk.Frame(window)
fixed_frame.grid(row=0, column=0, sticky=tk.W + tk.E)

# "Run input code" button config
btn_File = tk.Button(fixed_frame, text='Run input code',
                     command=lambda: worse(inputbox.get('1.0', 'end-1c'), morse_state.get()))
btn_File.grid(row=0, column=0, padx=(10), pady=10)

# "Enable morse" checkbox config
morse_state = tk.BooleanVar()
morse_state.set(True)
morse_chk = tk.Checkbutton(fixed_frame, text="Enable morse", var=morse_state, command=switch_input)
morse_chk.grid(row=0, column=1, padx=(10), pady=10)

# "Interpreter mode" checkbox config
inter_state = tk.BooleanVar()
inter_state.set(True)
inter_chk = tk.Checkbutton(fixed_frame, text="Interpreter mode", var=inter_state)
inter_chk.grid(row=0, column=2, padx=(10), pady=10)

# "Input code" textbox config
group1 = tk.LabelFrame(window, text="Input code", padx=5, pady=5)
group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
group1.rowconfigure(0, weight=1)
group1.columnconfigure(0, weight=1)
inputbox = scrolledtext.ScrolledText(group1, width=40, height=10)
inputbox.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

# "Output" textbox config
group2 = tk.LabelFrame(window, text="Output", padx=5, pady=5)
group2.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)
window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
group2.columnconfigure(0, weight=1)
outputbox = scrolledtext.ScrolledText(group2, width=40, height=10)
outputbox.configure(state="disabled")
outputbox.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

# Start gui
if __name__ == "__main__":
    window.mainloop()
