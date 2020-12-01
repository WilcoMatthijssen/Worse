def worse(text, is_morse=False):
    from runner import runner, RunnerError
    from parse import parser, ParserError
    from lexer import lexer, TokenSpecies, LexerError, morse_converter

    text = morse_converter(text) if is_morse else text

    try:
        tokens = lexer(text, TokenSpecies, r"[^\:\=\!\+\-\(\)\,\;\?\s\w]")

        ast = parser(tokens)

        print(runner(ast, "main"))


    except LexerError as e:

        gui_print(f"MESSED UP AT PARSING BECAUSE: {e}")

        print(f"MESSED UP AT LEXING BECAUSE: {e}")


    except ParserError as e:

        gui_print(f"MESSED UP AT PARSING BECAUSE: {e}")

        print(f"MESSED UP AT PARSING BECAUSE: {e}")


    except RunnerError as e:

        gui_print(f"MESSED UP AT RUNNING BECAUSE: {e}")

        print(f"MESSED UP AT RUNNING BECAUSE: {e} \n")



import tkinter as tk
from tkinter import scrolledtext


def gui_print(text: str):
    outputbox.insert(tk.END, text + "\n")

file = open("actual_worse.txt")
file_contents = file.read()
file.close()

window = tk.Tk()
window.title("Worse IDE")
window.geometry("900x400")

fixed_frame = tk.Frame(window)

fixed_frame.grid(row=0, column=0, sticky=tk.W + tk.E)

btn_File = tk.Button(fixed_frame, text='Run Worse code',
                     command=lambda: worse(inputbox.get('1.0', 'end-1c'), morse_state.get()))
btn_File.grid(row=0, column=0, padx=(10), pady=10)

morse_state = tk.BooleanVar()
morse_state.set(False)
morse_chk = tk.Checkbutton(fixed_frame, text="Enable morse", var=morse_state)
morse_chk.grid(row=0, column=1, padx=(10), pady=10)

inter_state = tk.BooleanVar()
inter_state.set(True)
inter_chk = tk.Checkbutton(fixed_frame, text="Interpreter mode", var=inter_state)
inter_chk.grid(row=0, column=2, padx=(10), pady=10)

group1 = tk.LabelFrame(window, text="Input code", padx=5, pady=5)
group1.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)

window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

group1.rowconfigure(0, weight=1)
group1.columnconfigure(0, weight=1)


inputbox = scrolledtext.ScrolledText(group1, width=40, height=10)
inputbox.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)

###################

group2 = tk.LabelFrame(window, text="Output", padx=5, pady=5)
group2.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tk.E + tk.W + tk.N + tk.S)

window.columnconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

group2.rowconfigure(0, weight=1)
group2.columnconfigure(0, weight=1)

# Create the textbox
outputbox = scrolledtext.ScrolledText(group2, width=40, height=10)
#outputbox.configure(state="disabled")
outputbox.grid(row=0, column=0, sticky=tk.E + tk.W + tk.N + tk.S)


def main():
    window.mainloop()




