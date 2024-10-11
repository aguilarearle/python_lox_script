
import Expr
from TokenType import *
import Token
from ErrorReporter import LoxRuntimeError, ErrorHandling
import Stmt
from typing import List
import Environment

class Interpreter(Expr.Visitor[object], Stmt.Visitor[None]):

    def __init__(self):
        self.environment = Environment.Environment()

    def interpret(self, statements: List[Stmt.Stmt]):
        try: 
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as error:
            ErrorHandling.runtimeError(error)

    def visitWhileStmt(self, stmt: Stmt.While) -> None:
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        
        return None

    def visitIfStmt(self, stmt: Stmt.If) -> None:
        if self.isTruthy(stmt.condition):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch:
            self.execute(stmt.elseBranch)
        return None

    def visitLogicalExpr(self, expr: Expr.Logical) -> object:
        left: object = self.evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self.isTruthy(expr.left): return left 
        else:
            if not self.isTruthy(expr.left): return left
        
        return self.evaluate(expr.right)
    
    def visitTernaryExpr(self, expr: Expr.Ternary) -> object:
        condition: object = self.evaluate(expr.condition)
        trueBranch: object = self.evaluate(expr.trueExpr)
        falseBranch: object = self.evaluate(expr.falseExpr)
        if condition == True:
            return trueBranch
        else:
            return falseBranch
            
    def visitLiteralExpr(self, expr: Expr.Literal) -> object:
        return expr.value
    
    def visitUnaryExpr(self, expr: Expr.Unary) -> object:
        right: object = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.isTruthy(right)
            case TokenType.MINUS:
                self.checkNumberOperand(expr.operator, right)
                return - float(right)

        return None
    
    def visitVariableExpr(self, expr: Expr.Variable) -> object:
        return self.environment.get(expr.name)
    
    def visitGroupingExpr(self, expr: Expr.Grouping) -> object:
        return self.evaluate(expr)    
    
    def checkNumberOperand(self, operator: Token, operand: object):
        if isinstance(operand, float): return
        raise LoxRuntimeError(operator, "Operand must be a number.")
    
    def checkNumberOperands(self, operator: Token, left: object, right: object):
        if isinstance(left, float) and isinstance(right, float): return

        raise LoxRuntimeError(operator, "Operands must be numbers.")
    
    def checkNumberZero(self, operator: Token, right: object):
        if isinstance(right, float) and right != 0: return
        raise LoxRuntimeError(operator, "Division by 0 not allowed")
        
    def visitBinaryExpr(self, expr: Expr.Binary) -> object:
        left: object = self.evaluate(expr.left)
        right: object = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.GREATER:
                self.checkNumberOperands(expr.operator, left, right)
                return float(left) > float(right)
            case TokenType.GREATER_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)                
                return float(left) >= float(right)
            case TokenType.LESS:
                self.checkNumberOperands(expr.operator, left, right)                
                return float(left) < float(right)
            case TokenType.LESS_EQUAL:
                self.checkNumberOperands(expr.operator, left, right)                
                return float(left) <= float(right)
            case TokenType.BANG_EQUAL:
                return not self.isEqual(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.isEqual(left, right)                            
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return float(left) + float(right)
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(int(right))
                raise LoxRuntimeError(expr.operator, "Operands must two numbers or two strings")              
            case TokenType.MINUS:
                self.checkNumberOperands(expr.operator, left, right)                
                return float(left) - float(right) 
            case TokenType.STAR:
                self.checkNumberOperands(expr.operator, left, right)                
                return float(left) * float(right)
            case TokenType.SLASH:
                self.checkNumberOperands(expr.operator, left, right)
                self.checkNumberZero(expr.operator,right)
                return float(left) / float(right)  
    
    def isEqual(self, left: object, right: object) -> bool:
        if left == None and right == None: return True
        if left == None: return False

        return left == right
    
    def stringify(self, obj: object) -> str:
        if obj == None: 
            return "nil"

        if isinstance(obj, float):
            text = str(obj)
            if text.endswith(".0"):  # For integers stored as floats
                text = text[0: len(text) - 2]
            return text

        return str(obj)    
    
    def isTruthy(self, obj: object):
        if obj == None:
            return False
        
        if isinstance(obj, bool): return bool(obj)
        
        return True
    
    def evaluate(self, expr: Expr.Expr):
        return expr.accept(self)
    
    def execute(self, stmt: Stmt.Stmt):
        stmt.accept(self)

    def executeBlock(self, statements: List[Stmt.Stmt], environment: Environment):
        previous: Environment = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visitBlockStmt(self, stmt: Stmt.Block) -> None:
        self.executeBlock(stmt.statements, Environment.Environment(self.environment))
        return None
    
    def visitExpressionStmt(self, stmt: Stmt.Expression) -> None:
        self.evaluate(stmt.expression)
        return None

    def visitPrintStmt(self, stmt: Stmt.Print) -> None:
        value: object = self.evaluate(stmt.expression)

        print(self.stringify(value))

        return None
    
    def visitVarStmt(self, stmt: Stmt.Var) -> None:
        value: object = None
        if stmt.initializer:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visitAssignExpr(self, expr: Expr.Assign) -> object:
        value: object = self.evaluate(expr.value)
        self.environment.assign(expr.name, value);
        return value
