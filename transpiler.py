from email.mime import message
from ast_printer import printAst

class Transpiler:
    def __init__(self) -> None:
        self.had_error = False

    
    def transpile(self, source_code: str) -> str:

        # lexer
        from lexer import Lexer
        lexer = Lexer(source_code, self)
        tokens = lexer.lexerize()

        # parser
        from parser import Parser
        parser = Parser(tokens, self)
        ast = parser.parse()

        # interpreter / code generator
        from codegen import CodeGenerator
        codegenerator = CodeGenerator()
        sql_string = codegenerator.generate(ast)

        return sql_string
    
    def error(self, line: int, message: str) -> None:
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str) -> None:
        print("[line " + str(line) + "] Error" + where + ":" + message)
        had_error = True

    def transpile_to_ast(self, source_code):
        """Just return AST witnou code generation (for testing)"""
        from lexer import Lexer
        from parser import Parser

        lexer = Lexer(source_code, self)
        tokens = lexer.lexerize()

        if self.had_error:
            return None
        
        parser = Parser(tokens, self)
        ast = parser.parse()

        return ast