class Program:
    # root node
    def __init__(self, statements: list) -> None:
        self.statements = statements

class VarDecl:
    # int x = 5;
    def __init__(self, type: str, name: str, init_val: object) -> None:
        self.type = type
        self.name = name
        self.init_val = init_val

class Assignment:
    # x = 10;
    def __init__(self, name: str, exp):
        self.name = name
        self.exp = exp

class PrintStmt:
    # print(x)
    def __init__(self, exp):
        self.exp = exp

class BinaryOp:
    # a + b
    def __init__(self, left, op, right):
        self.left_op = left
        self.op = op
        self.right_op = right

class Literal:
    # 5, "hello"
    def __init__(self, value) -> None:
        self.value = value

class Variable:
    # x 
    def __init__(self, name: str) -> None:
        self.name = name

class Grouping:
    def __init__(self, expression) -> None:
        self.expression = expression

class UnaryOp:
    def __init__(self, op, expression) -> None:
        self.op = op
        self.expression = expression

class IfStmt:
    def __init__(self, condition, then_branch, else_branch) -> None:
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        
class WhileStmt: 
    def __init__(self, condition, body) -> None:
        self.condition = condition
        self.body = body

class SelectStmt:
    def __init__(self, fields : list, table: str, where_clause) -> None:
        self.fields = fields
        self.table = table
        self.where_clause = where_clause

class ForeachStatement:
    def __init__(self, fields : list, body, selectStmt) -> None:
        self.fields = fields
        self.body = body
        self.selectStmt = selectStmt