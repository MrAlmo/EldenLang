import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename.el>")
        return

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    try:
        tokens = Lexer(source).tokenize()

        ast = Parser(tokens).parse()

        interpreter = Interpreter()
        interpreter.run(ast)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()