import sys
from ast_nodes import *

class CodeGenerator:
    OPERATOR_MAP = {
        '==': '=',
        '!=': '<>',
        'and': 'AND',
        'or': 'OR'
    }

    LOGICAL_OPS = {
        'and', 'or', '!', 'not'
    }

    COMPARISON_OPS = {
        '==', '!=', '>', '<', '>=', '<='
    }

    OPERATORS = LOGICAL_OPS | COMPARISON_OPS

    def __init__(self):
        self.output = []
        self.label_counter = 1
        self.cursor_counter = 1
        self.symbol_table = {}

    def generate(self, program):
        # Takes Program AST node, Returns Priority SQL String
        if (not isinstance(program, Program)):
            print("Not a program")
            sys.exit(65)

        for statement in program.statements:
            self.generate_statement(statement)

        return "\n".join(self.output)
    
    def generate_foreach_statement(self, foreachStatement):
        fields_sql = ""
        if (foreachStatement.fields):
            for field in foreachStatement.fields:
                fields_sql += field + ", "
            fields_sql = fields_sql[:-2]

        cursor_label = self.cursor_counter
        self.cursor_counter += 1

        begin_label = self.label_counter
        self.label_counter += 1
        end_label = self.label_counter
        self.label_counter += 1
        error_label = self.label_counter

        self.output.append(f"DECLARE c{cursor_label} CURSOR FOR ")
        self.generate_select_statement(foreachStatement.selectStmt, 'foreach')

        self.output.append(f"")
        self.output.append(f"OPEN C{cursor_label};")
        self.output.append(f"GOTO {error_label} WHERE :REVAL < 0;")

        self.output.append(f"")
        self.output.append(f"LABEL {begin_label};")

        vars = ""
        for var_label in range(1, len(foreachStatement.selectStmt.fields) + 1):
            vars += ":VAR" + str(var_label) + ", "
        self.output.append(f"FETCH C{cursor_label} INTO {vars[:-2]};")


        self.output.append(f"GOTO {error_label} WHERE :RETVAL < 0;")


        self.output.append(f"")
        for st in foreachStatement.body:
            self.generate_statement(st)
        self.output.append(f"")

        self.output.append(f"LOOP {begin_label};")
        self.output.append(f"")

        self.output.append(f"LABEL {end_label};")
        self.output.append(f"CLOSE C{cursor_label};")
        self.output.append(f"LABEL {error_label};")

        return "\n".join(self.output)
    


    def generate_select_statement(self, selectStatement, context='condition'):
        # context = 'condition' # double check

        fields_sql = ""
        if (selectStatement.fields):
            for field in selectStatement.fields:
                fields_sql += field + ", "
            fields_sql = fields_sql[:-2]

        where_complement = ""
        if (selectStatement.where_clause):
            where_complement = self.generate_expression(selectStatement.where_clause, context)
            where_complement = f" WHERE {where_complement}"
        self.output.append(f"SELECT {fields_sql} FROM {selectStatement.table}{where_complement};")


    def genereta_while_statement(self, whileStatement):
        context = 'condition'
        condition = self.generate_expression(whileStatement.condition, context)

        begin_label = self.label_counter
        self.label_counter += 1
        end_label = self.label_counter
        self.label_counter += 1

        self.output.append(f"LABEL {begin_label};")
        self.output.append(f"GOTO {end_label} WHERE NOT ({condition});")
        if whileStatement.body:
            for statement in whileStatement.body:
                self.generate_statement(statement)
        self.output.append(f"LOOP {begin_label};")
        self.output.append(f"LABEL {end_label};")


    def generate_if_statement(self, ifStatement):
        context = 'condition'
        condition = self.generate_expression(ifStatement.condition, context)

        # Always need at least one label (for else/end)
        else_label = self.label_counter
        self.label_counter += 1

        # Only need end_label if there's an else branch
        if ifStatement.else_branch:
            end_label = self.label_counter
            self.label_counter += 1

        # Jump to else/end if condition false
        self.output.append(f"GOTO {else_label} WHERE NOT ({condition});")

        # The branch
        for statement in ifStatement.then_branch:
            self.generate_statement(statement)
        
        # If else exists: skip it and add else statements
        if ifStatement.else_branch:
            self.output.append(f"GOTO {end_label};")
            self.output.append(f"LABEL {else_label};")
            for statement in ifStatement.else_branch:
                self.generate_statement(statement)
            self.output.append(f"LABEL {else_label};")
        else:
            # No else: just the end label (which is else_label)
            self.output.append(f"LABEL {else_label};")

    def generate_statement(self, statement):
        if isinstance(statement, PrintStmt):
            expr_sql = self.generate_expression(statement.exp)
            self.output.append(f"SELECT {expr_sql} FROM DUMMY ASCII;")

        elif isinstance(statement, Assignment):
            expr_sql = self.generate_expression(statement.exp)
            self.output.append(f":{statement.name} = {expr_sql};")

        elif isinstance(statement, VarDecl):
            expr_sql = self.generate_expression(statement.init_val)
            self.output.append(f":{statement.name} = {expr_sql};")

        elif isinstance(statement, Grouping):
            expr_sql = self.generate_expression(statement.exp)
            self.output.append(f"{expr_sql}")

        elif isinstance(statement, IfStmt):
            self.generate_if_statement(statement)

        elif isinstance(statement, WhileStmt):
            self.generate_while_statement(statement)
            
        elif isinstance(statement, SelectStmt):
            self.generate_select_statement(statement)

        elif isinstance(statement, ForeachStatement):
            self.generate_foreach_statement(statement)

        else:
                print(f"Unknown")

    def generate_expression(self, expr, context='value'):
        """
        Generate SQL for an expression.
        
        Args:
            expr: AST expression node
            context: 'value' (assignment/print) or 'condition' (if/while)
        """
        # --- BinaryOp ---
        if isinstance(expr, BinaryOp):

            left = self.generate_expression(expr.left_op, context)
            right = self.generate_expression(expr.right_op, context)
            op = self.OPERATOR_MAP.get(expr.op.lexeme, expr.op.lexeme)


            if expr.op.lexeme in self.OPERATORS and context == 'value':
                return f"({left} {op} {right} ? 1 : 0)"
            
            return f"{left} {op} {right}"
        
        # --- Literal ---
        elif isinstance(expr, Literal):
            if (isinstance(expr.value, str)):
                return f"'{expr.value}'"
            else:
                return f"{expr.value}"

        # --- Variable ---
        elif isinstance(expr, Variable):
            if context == 'value':
                return f":{expr.name}"
            else: 
                return f"{expr.name}"
        
        # --- Grouping ---
        elif isinstance(expr, Grouping):
            expression = self.generate_expression(expr.expression, context)
            return f"({expression})"

        # --- Unary ---
        elif isinstance(expr, UnaryOp):
            operand = self.generate_expression(expr.expression, context)
            op = expr.op.lexeme

            if isinstance(expr.expression, (Literal, Variable, Grouping)):
                return f"{op}{operand}"
            else:
                return f"{op}({operand})"