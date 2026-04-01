import ast_nodes

def printAst(ast, indent=0) -> None:
    prefix = " " * indent

    if isinstance(ast, ast_nodes.Program):
        print(f"{prefix}Program")
        for stmt in ast.statements:
            printAst(stmt, indent + 1)

    elif isinstance(ast, ast_nodes.Literal):
        print(f"{prefix}Literal({ast.value})")

    elif isinstance(ast, ast_nodes.Variable):
        print(f"{prefix}Variable({ast.name})")

    elif isinstance(ast, ast_nodes.BinaryOp):
        print(f"{prefix}BinaryOp({ast.value})")
        printAst(ast.left_op, indent + 1)
        printAst(ast.right_op, indent + 1)
    
    elif isinstance(ast, ast_nodes.PrintStmt):
        print(f"{prefix}PrintStmt")
        printAst(ast.exp, indent + 1)

    elif isinstance(ast, ast_nodes.Assignment):
        print(f"{prefix}Assignment({ast.name})")
        printAst(ast.exp, indent + 1)

    elif isinstance(ast, ast_nodes.VarDecl):
        print(f"{prefix}VarDecl({ast.type} {ast.name})")
        printAst(ast.init_val, indent + 1)
    
    else:
        print(f"{prefix}Inknown: {type(ast).__name__}")