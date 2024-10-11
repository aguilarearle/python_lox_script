from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
import Token
R = TypeVar('R')

class Expr(ABC):
    def accept(self, visitor: 'Visitor[R]') -> R:
        pass

class Visitor(Generic[R]):
    def visitTernaryExpr(self, Expr: 'Ternary') -> R:
        pass
    def visitAssignExpr(self, Expr: 'Assign') -> R:
        pass
    def visitBinaryExpr(self, Expr: 'Binary') -> R:
        pass
    def visitCallExpr(self, Expr: 'Call') -> R:
        pass
    def visitGroupingExpr(self, Expr: 'Grouping') -> R:
        pass
    def visitLiteralExpr(self, Expr: 'Literal') -> R:
        pass
    def visitLogicalExpr(self, Expr: 'Logical') -> R:
        pass
    def visitUnaryExpr(self, Expr: 'Unary') -> R:
        pass
    def visitVariableExpr(self, Expr: 'Variable') -> R:
        pass

class Ternary(Expr):
    def __init__(self, condition: Expr, trueExpr: Expr, falseExpr: Expr):
        self.condition = condition
        self.trueExpr = trueExpr
        self.falseExpr = falseExpr

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitTernaryExpr(self)

class Assign(Expr):
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitAssignExpr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitBinaryExpr(self)

class Call(Expr):
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitCallExpr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __init__(self, value: object):
        self.value = value

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitLiteralExpr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitLogicalExpr(self)

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitUnaryExpr(self)

class Variable(Expr):
    def __init__(self, name: Token):
        self.name = name

    def accept(self, visitor: 'Visitor[R]') -> R:
        return visitor.visitVariableExpr(self)

