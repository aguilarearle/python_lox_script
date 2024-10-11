from TokenType import *
from typing import List
from Token import Token
import Expr
import Stmt
from ErrorReporter import ErrorHandling

class ParseError(RuntimeError):
    pass

class Parser:

    def __init__(self, tokens: List[Token]):
        self.current = 0
        self.tokens = tokens

    def parse(self) -> Expr.Expr:
        statements: Stmt = []

        while not self.isAtEnd():
            statements.append(self.declaration())
        
        return statements
    
    def expression(self) -> Expr.Expr:
        return self.assignment()
    
    def declaration(self) -> Stmt.Stmt:
        try:
            if self.match(TokenType.VAR): return self.varDeclaration()
            return self.statement()
        except ParseError as error:
            self.synchronize()
            return None

    def statement(self):
        if self.match(TokenType.FOR): return self.forStatement()
        if self.match(TokenType.IF): return self.ifStatement()
        if self.match(TokenType.PRINT): return self.printStatement()
        if self.match(TokenType.WHILE): return self.whileStatement()
        if self.match(TokenType.LEFT_BRACE): return Stmt.Block(self.block())
        return self.expressionStatement()
    
    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'")
        initializer: Stmt.Stmt

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()
        
        print(f"initializer: {initializer}")
        condition: Expr.Expr

        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after loop condition.")

        increment: Expr.Expr
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expected ')' after for clauses.")
        body: Stmt.Stmt = self.statement()

        if increment != None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        if condition == None: 
            condition = Expr.Literal(True)
        body = Stmt.While(condition, body)

        if initializer != None:
            body = Stmt.Block([initializer, body])

        return body

    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.LEFT_PAREN, "Expect ')' after condition.")
        body: Stmt.Stmt = self.statement()

        return Stmt.While(condition, body)        
    
    def ifStatement(self) -> Stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'")
        condition: Expr.Expr = self.expression()
        self.consume(TokenType.LEFT_PAREN, "Expect ')' after if condition.")

        thenBranch: Stmt.Stmt = self.statement()
        elseBranch: Stmt.Stmt = None

        if self.match(TokenType.ELSE):
            elseBranch = self.statement

        return Stmt.If(condition, thenBranch, elseBranch)
    
    def printStatement(self) -> Stmt.Stmt:
        value: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")

        return Stmt.Print(value)
    
    def varDeclaration(self) -> Stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expected variable name.")

        initializer: Expr = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        return Stmt.Var(name, initializer) 
    
    def expressionStatement(self) -> Stmt.Stmt:
        expr: Expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")

        return Stmt.Expression(expr)
    
    def block(self) -> List[Stmt.Stmt]:
        statements: List[Stmt.Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return statements
    
    def assignment(self) -> Expr.Expr:
        expr: Expr.Expr = self.Or() # was ternary

        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: Expr.Expr = self.assignment()

            if isinstance(expr, Expr.Variable):
                name: Token = expr.name
                return Expr.Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def Or(self):
        expr: Expr = self.And()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: Expr = self.And()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    def And(self):
        expr: Expr = self.ternary()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: Expr = self.ternary()
            expr = Expr.Logical(expr, operator, right)
        
        return expr
    
    def ternary(self) -> Expr.Expr:
        expr: Expr.Expr = self.equality()

        if self.match(TokenType.QUESTION):
            trueBranch = self.expression()            
            self.consume(TokenType.COLON, "Expect ':' after ternary.")            
            falseBranch = self.expression()

            expr = Expr.Ternary(expr, trueBranch, falseBranch)
        return expr
    
    def equality(self) -> Expr.Expr:
        expr: Expr.Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        
        return expr

    def comparison(self) -> Expr.Expr:
        expr: Expr.Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: Expr.Expr = self.term()
            expr = Expr.Binary(expr, operator, right)

        return expr
    
    def term(self) -> Expr.Expr:
        expr: Expr.Expr = self.factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.factor()
            expr = Expr.Binary(expr, operator, right)
        return expr
    
    def factor(self) -> Expr.Expr:
        expr: Expr.Expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr.Expr = self.unary()
            expr = Expr.Binary(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr.Expr = self.primary()
            return Expr.Unary(operator, right)
        
        return self.call()

    def call(self) -> Expr.Expr:
        expr: Expr.Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break
        
        return expr
    
    def finishCall(self, calle: Expr) -> Expr.Expr:
        arguments: List[Expr.Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return Expr.Call(callee,token,arguments)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE): return Expr.Literal(False)
        if self.match(TokenType.TRUE): return Expr.Literal(True)
        if self.match(TokenType.NIL): return Expr.Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr: Expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Expr.Grouping(expr)                
        
        raise self.error(self.peek(), "Expect expression.")

    def match(self, *types: TokenType) -> bool:
        for type in types:
            if self.check(type):
                self.advance()
                return True
            
        return False
    
    def error(self, token: Token, message: str) -> ParseError:
        ErrorHandling.error(token, message)
        return ParseError()
    
    def synchronize(self):
        self.advance()

        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON: return

            match self.peek().type:
                case TokenType.CLASS | TokenType.FOR | TokenType.FUN | TokenType.IF \
                    | TokenType.PRINT | TokenType.RETURN | TokenType.VAR | TokenType.WHILE:
                    return
                
            self.advance()
        
    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def check(self, type: TokenType) -> bool:
        if self.isAtEnd(): 
            return False
        
        return self.peek().type == type

    def advance(self) -> Token:
        if not self.isAtEnd():
            self.current += 1

        return self.previous()
    
    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
