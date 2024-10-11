from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
import Token
import Expr
R = TypeVar('R')

class Stmt(ABC):
    def accept(self, visitor: 'Visitor[R]') -> R:
        pass

class Visitor(Generic[R]):
    def visitBlockStmt(self, Stmt: 'Block') -> R:
        pass
    def visitExpressionStmt(self, Stmt: 'Expression') -> R:
        pass
    def visitIfStmt(self, Stmt: 'If') -> R:
        pass
    def visitPrintStmt(self, Stmt: 'Print') -> R:
        pass
    def visitWhileStmt(self, Stmt: 'While') -> R:
        pass
    def visitVarStmt(self, Stmt: 'Var') -> R:
        pass

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitBlockStmt(self)

class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitExpressionStmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseBranch: Stmt):
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitIfStmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitPrintStmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitWhileStmt(self)

class Var(Stmt):
    def __init__(self, name: Token, initializer: Expr):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitVarStmt(self)

