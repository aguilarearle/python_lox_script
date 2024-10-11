from TokenType import TokenType

class Token:
    def __init__(self, tType: TokenType, lexeme: str, literal: object, line: int):
        self.type = tType
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f'{self.type} {self.lexeme} {self.literal}'