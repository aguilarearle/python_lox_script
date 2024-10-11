from typing import List, Generic, TypeVar

class PrintWriter:
    def __init__(self, path):
        self.file = open(path, "w")  # Open the file for writing
    
    def println(self, text=""):
        self.file.write(str(text) + "\n")  # Write the text followed by a newline
    
    def close(self):
        self.file.close()  # Close the file when done

class GenerateAst:
    @staticmethod
    def main(args: List[str]):
        if len(args) != 1:
            print("Usage: generate_ast <output_dir>")
            exit(64)
        
        outputDir = args[0]

        GenerateAst.defineAst(outputDir, "Expr", [
            "Ternary  -> condition: Expr, trueExpr: Expr, falseExpr: Expr",   
            "Assign   -> name: Token, value: Expr",
            "Binary   -> left: Expr, operator: Token, right: Expr",
            "Call     -> callee: Expr, paren: Token, arguments: List[Expr]", 
            "Grouping -> expression: Expr",
            "Literal  -> value: object",
            "Logical  -> left: Expr, operator: Token, right: Expr",
            "Unary    -> operator: Token, right: Expr",
            "Variable -> name: Token"
        ])

        GenerateAst.defineAst(outputDir, "Stmt", [
            "Block      -> statements: List[Stmt]",
            "Expression -> expression: Expr",
            "If         -> condition: Expr, thenBranch: Stmt, elseBranch: Stmt",
            "Print      -> expression: Expr",
            "While      -> condition: Expr, body: Stmt",
            "Var        -> name: Token, initializer: Expr"
        ])

    @staticmethod
    def defineAst(outputDir: str, baseName: str, types: List[str]):
        path: str = f"{outputDir}/{baseName}.py"
        writer: PrintWriter = PrintWriter(path)

        writer.println("from abc import ABC, abstractmethod")
        writer.println("from typing import Generic, TypeVar, List")
        writer.println("import Token")        
        if baseName == "Stmt":
            writer.println("import Expr")            
        writer.println("R = TypeVar('R')")

        writer.println()
        writer.println(f"class {baseName}(ABC):")
        writer.println(f"    def accept(self, visitor: 'Visitor[R]') -> R:")
        writer.println("        pass")        
        writer.println()

        GenerateAst.defineVisitor(writer, baseName, types)

        # The AST classes
        for type in types:
            className, fields = [part.strip() for part in type.split("->")]
            GenerateAst.defineType(writer, baseName, className, fields)

        writer.close()
    
    @staticmethod
    def defineVisitor(writer: PrintWriter, baseName: str, types:  List[str]):
        writer.println("class Visitor(Generic[R]):")

        for type in types:
            typeName, _ = [part.strip() for part in type.split("->")]
            writer.println(f"    def visit{typeName}{baseName}(self, {baseName}: '{typeName}') -> R:")
            writer.println("        pass")
        writer.println()
        
    @staticmethod
    def defineType(writer: PrintWriter, baseName: str, className: str, fieldList: str):
        writer.println(f"class {className}({baseName}):")

        writer.println(f"    def __init__(self, {fieldList}):")

        fields = fieldList.split(", ")
        for field in fields:
            name = field.split(": ")[0]
            writer.println(f"        self.{name} = {name}")
        writer.println()
        writer.println(f"    def accept(self, visitor: 'Visitor[R]') -> R:")
        writer.println(f"        return visitor.visit{className}{baseName}(self)")
        writer.println()
    
             
if __name__ == "__main__":
    import sys
    GenerateAst.main(sys.argv[1:])
