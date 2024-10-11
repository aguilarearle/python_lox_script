import Expr
from TokenType import *
from Token import Token
from typing import List

class AstPrinter(Expr.Visitor[str]):

    @staticmethod
    def main(args: List[str]):
        expression: Expr = Expr.Binary(
            Expr.Unary(
                Token(TokenType.MINUS, "-", None, 1),
                Expr.Literal(123)
            ),
            Token(TokenType.STAR, "*", None, 1),
            Expr.Grouping(
                Expr.Literal(45.67)
            )
        )

        print(AstPrinter().print(expression))

    def print(self, expr: Expr) -> str:
        return expr.accept(self)
    
    def visitBinaryExpr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)
    
    def visitTernaryExpr(self, expr: Expr.Ternary) -> str:
        return self.parenthesize("?",expr.condition, expr.trueExpr, expr.falseExpr)

    def visitUnaryExpr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def visitLiteralExpr(self, expr: Expr.Literal) -> str:
        if expr.value == None:
            return 'nil'
        return str(expr.value)

    def visitGroupingExpr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)
    
    def parenthesize(self, name: str, *exprs: Expr):
        builder = ""
        builder += f"({name}"
        for expr in exprs:
            builder += " "
            builder += expr.accept(self)
        
        builder += ")"

        return builder
    
if __name__ == "__main__":
    import sys
    AstPrinter.main(sys.argv[1:])    