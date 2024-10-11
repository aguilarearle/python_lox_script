from TokenType import *
from Token import Token
from typing import List, Dict, Optional
from ErrorReporter import ErrorHandling

class Scanner: 

    def __init__(self, source: str, tokens: Optional[List[Token]] = None):
        self.source = source
        self.tokens = tokens if tokens is not None else []
        
        # start and current are offsets that index into the string
        # start -> first character in the lexme
        # current -> current scanned character
        self.start: int = 0
        self.current: int = 0
        # source code line
        self.line: int = 1
        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "return": TokenType.RETURN,
            "super": TokenType.SUPER,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE
        }          

    def scanTokens(self) -> List[Token]:
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scanToken(self):
        c: str = self.advance()
        
        match c:
            case '(': self.addToken(TokenType.LEFT_PAREN)
            case ')': self.addToken(TokenType.RIGHT_PAREN)
            case '{': self.addToken(TokenType.LEFT_BRACE)
            case '}': self.addToken(TokenType.RIGHT_BRACE)
            case ',': self.addToken(TokenType.COMMA)
            case '.': self.addToken(TokenType.DOT)
            case '-': self.addToken(TokenType.MINUS)
            case '+': self.addToken(TokenType.PLUS)
            case ';': self.addToken(TokenType.SEMICOLON)
            case '*': self.addToken(TokenType.STAR)
            case '?': self.addToken(TokenType.QUESTION)
            case ':': self.addToken(TokenType.COLON)
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=': 
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '/':
                if self.match('/'):
                    while self.peek() != '\n' and not self.isAtEnd(): 
                        self.advance()
                elif self.match('*'):
                    while self.peek() != '/'  and not self.isAtEnd():
                        self.advance()
                    self.advance()
                else:
                    self.addToken(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _:  
                if c.isdigit():
                    self.number()
                elif self.isAlpha(c):
                    self.identifier()
                else:
                    ErrorHandling.error(self.line, 'Unexpected character.')
    
    def isAlpha(self, c: str) -> bool:
        return c.isalpha() or c == '_'
    
    def isAlphaNumeric(self, c: str) -> bool:
        return self.isAlpha(c) or c.isdigit()
    
    def identifier(self):
        while self.isAlphaNumeric(self.peek()):
            self.advance()
        
        text: str = self.source[self.start:self.current]

        if text not in self.keywords:
            type = TokenType.IDENTIFIER
        else:
            type = self.keywords[text]
        
        self.addToken(type)

    def number(self):
        while self.peek().isdigit():
            self.advance()
        
        if self.peek() == '.' and self.peekNext().isdigit():
            self.advance()

            while self.peek().isdigit():
                self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start: self.current]))

    def string(self):
        while self.peek() != '"' and not self.isAtEnd():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.isAtEnd():
            ErrorHandling.error(self.line, "Unterminated string.")
            return
        
        self.advance()

        value: str = self.source[self.start + 1: self.current - 1]
        self.addToken(TokenType.STRING, value)

    def match(self, expected: str) -> bool:
        if self.isAtEnd():
            return False
    
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True
                
    def peek(self) -> str:
        if self.isAtEnd(): 
            return '\0'
        
        return self.source[self.current]
    
    def peekNext(self) -> str:
        if self.current >= len(self.source):
            return '\0'
        
        return self.source[self.current + 1]
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def addToken(self, type: TokenType, literal: object = None):
        text = self.source[self.start: self.current]
        self.tokens.append(Token(type, text, literal, self.line))
        
    def isAtEnd(self):
        return self.current >= len(self.source)
