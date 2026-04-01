#!/usr/bin/env python3
import sys
from transpiler import Transpiler

def main(filename: str) -> None:
    # if not os.path.exists(filename):
    #     print(f"X {filename}: sSource file not found")
    #     return
    try:
        with open(f"{filename}", "r") as file:
            source = file.read()

    except FileNotFoundError:
        print(f"File {filename}.stc not found.")

    except Exception as e:
        print(f"An error ocurred: {e}")

    # Create transpiler and run
    transpiler = Transpiler()
    result = transpiler.transpile(source)

    if transpiler.had_error:
        sys.exit(65)

    # Print the generated Priority SQL
    print(result)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        arg1 = sys.argv[1]
    else:
        print("Usage: python3 main.py <filename>")
        exit(1)

    main(arg1)