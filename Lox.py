import os
from typing import List
import Scanner
from Token import Token
from TokenType import *
import Parser
import Stmt
from AstPrinter import AstPrinter
from ErrorReporter import ErrorHandling
from Interpreter import Interpreter
directory = "/lox_script/"

class Lox:

    interpreter: Interpreter = Interpreter()

    @staticmethod
    def main( args: List[str]):

        if len(args) > 1:
            print('Usage: jlox p[script]')
            exit(64)
        elif len(args) == 1:
            Lox.runFile(args)
        else:
            Lox.runPrompt()

    @staticmethod     
    def runFile(filename: str):
        script_directory = os.path.dirname(__file__)
        directory = os.path.join(script_directory, 'lox_script')        
        file_path = os.path.join(directory, filename[0])

        with open(file_path, 'r') as file:
            file_contents = file.read()

        # Print the file contents
        Lox.run(file_contents)

        if ErrorHandling.hadError: 
            exit(65)
        if ErrorHandling.hadRuntimeError:
            exit(70)

    @staticmethod    
    def runPrompt():
        print('Running prompt')
        while True:
            try:
                line = input("> ")

                if line in ["exit", "quit"]:
                    print("Exiting REPL...")
                    break

                Lox.run(line)
                ErrorHandling.hadError = False

            except EOFError:
                # Handle Ctrl+D (EOF)
                print("\nEnd of File (EOF) detected. Exiting REPL...")
                break

            except KeyboardInterrupt:
                # Handle Ctrl+C (interrupt)
                print("\nKeyboard Interrupt detected. Exiting REPL...")
                break

    @staticmethod
    def run(source: str):
        scanner: Scanner = Scanner.Scanner(source)
        tokens: List[Token] = scanner.scanTokens()
        parser: Parser = Parser.Parser(tokens)
        statements: Stmt.Stmt = parser.parse()


        if ErrorHandling.hadError: return

        Lox.interpreter.interpret(statements)
        
if __name__ == "__main__":
    import sys
    Lox.main(sys.argv[1:])