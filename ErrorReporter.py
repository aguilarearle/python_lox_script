# ErrorHandling.py

class LoxRuntimeError(RuntimeError):
    def __init__(self, token, message: str):
        super().__init__(message)
        self.message = message
        self.token = token  

class ErrorHandling:
    hadError = False
    hadRuntimeError = False
    @staticmethod
    def error(line: int, message: str):
        ErrorHandling.report(line, "", message)

    @staticmethod
    def report(line: int, where: str, message: str):
        print(f'[line {line}] Error {where}: {message}')
        ErrorHandling.hadError = True

    @staticmethod
    def runtimeError(error: LoxRuntimeError):
        print(f'{str(error)} \n [line {error.token.line}]')
        ErrorHandling.hadRuntimeError = True

    @staticmethod
    def error_with_token(token, message: str):
        if token.type == "EOF":
            ErrorHandling.report(token.line, " at end", message)
        else:
            ErrorHandling.report(token.line, f" at '{token.lexeme}'", message)

  