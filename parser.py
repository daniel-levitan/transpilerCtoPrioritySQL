from transpiler import Transpiler
from token_type import TokenType, Token
from ast_nodes import *

class Parser:
    def __init__(self, tokens: list, transpiler: Transpiler) -> None:
        self.tokens = tokens
        self.transpiler = transpiler
        self.current = 0

    def parse(self):
        return self.program()
    
    def primary(self):
        if (self.match(TokenType.NUMBER, TokenType.STRING)):
            return Literal(self.previous().literal)
        
        if (self.match(TokenType.IDENTIFIER)):
            return Variable(self.previous().lexeme)
        
        if (self.match(TokenType.LEFT_PAREN)):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        self.transpiler.error(self.peek().line, "Expect expression.")
        return None
    
    def unary(self):
        # -5
        if (self.match(TokenType.MINUS)):
            op = self.previous()
            right = self.unary()
            return UnaryOp(op, right)
        
        return self.primary()
    
    def factor(self):
        expr = self.unary()
        while (self.match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT)):
            operator = self.previous()
            right = self.unary()
            expr = BinaryOp(expr, operator, right)
        return expr
    
    def logical_or(self):
        expr = self.logical_and()

        while (self.match(TokenType.OR)):
            operator = self.previous()
            right = self.logical_and()
            expr = BinaryOp(expr, operator, right)

        return expr
    
    def logical_and(self):
        expr = self.equality()

        while (self.match(TokenType.AND)):
            operator = self.previous()
            right = self.equality()
            expr = BinaryOp(expr, operator, right)

        return expr
    
    def equality(self):
        expr = self.comparison()
        
        while (self.match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL)):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryOp(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.term()

        while (self.match(TokenType.GREATER, TokenType.GREATER_EQUAL,
                          TokenType.LESS, TokenType.LESS_EQUAL)):
            operator = self.previous()
            right = self.term()
            expr = BinaryOp(expr, operator, right)

        return expr
    
    def term(self):
        expr = self.factor()

        while (self.match(TokenType.MINUS, TokenType.PLUS)):
            operator = self.previous()
            right = self.factor()
            expr = BinaryOp(expr, operator, right)

        return expr
    
    def expression(self):
        return self.logical_or()
    
    def printStatement(self):
        # print ( expression ) ;

        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'print'.")

        value = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after value.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)
    
    def ifStatement(self):
        # if (condition) {} else {}

        # -- Condition
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after the condition.")

        # -- Then branch
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after ')'.")
        then_branch = []
        while (not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd()):
            then_branch.append(self.statement())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after then statements.")

        # -- Else branch
        else_branch = None
        if (self.match(TokenType.ELSE)):
            else_branch = []

            self.consume(TokenType.LEFT_BRACE, "Expect '{' after 'else'.")
            while (not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd()):
                else_branch.append(self.statement())
            self.consume(TokenType.RIGHT_BRACE, "Expect '}' after else statements.")

        return IfStmt(condition, then_branch, else_branch)
    
    def whileStatement(self):
        # -- ccondition
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after the condition.")

        # -- Body
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after ')'.")
        body = []
        while (not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd()):
            body.append(self.statement())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after else statements.")

        return WhileStmt(condition, body)
    
    def selectStatement(self, context='select'):
        # SELECT A, B FROM TABLE WHERE a > b;
        # fields, table, where_clause
        fields = []

        if (self.check(TokenType.STAR)):
            fields.append('*')
            self.advance()
        else:
            fields.append(self.consume(TokenType.IDENTIFIER, "Expect column name.").lexeme)
            while (not self.check(TokenType.COMMA) and not self.isAtEnd()):
                fields.append(self.consume(TokenType.IDENTIFIER, "Expect column name.").lexeme)
            
            self.consume(TokenType.FROM, "Expect from.")
            table = self.consume(TokenType.IDENTIFIER, "Expect table name.")

        
        where_clause = None
        if (self.match(TokenType.WHERE)):
            where_clause = self.epxression()

        if context == 'select':
            self.consume(TokenType.SEMICOLON, "Expect ';'")

        return SelectStmt(fields, table.lexeme, where_clause)
    
    def foreachStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'foreach'.")

        fields = []
        fields.append(self.consume(TokenType.IDENTIFIER, "Expect column name.").lexeme)
        while (not self.check(TokenType.COMMA) and not self.isAtEnd()):
            fields.append(self.consume(TokenType.IDENTIFIER, "Expect column name.").lexeme)
        
        self.consume(TokenType.IN, "Expect 'in' after the condition.")
        self.consume(TokenType.SELECT, "Expect 'select' after 'in'.")
        selectStmt = self.selectStatement('foreach')
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after the condition.")

        # body
        self.consume(TokenType.LEFT_BRACE, "Expect '{' after ')'.")
        body = []
        while (not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd()):
            body.append(self.statement())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after else statements.")

        return ForeachStatement(fields, body, selectStmt)

    def expressionStatement(self):
        # Parse: IDENTIFIER "=" expresion ";"

        # Get the variable name
        name_token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        # Consume the "="
        self.consume(TokenType.EQUAL, "Expect '=' in assignment.")

        # Parse the expression
        expr = self.expression()

        # Consume the ";""
        self.consume(TokenType.SEMICOLON, "Expect ';' after the expression.")

        return Assignment(name_token.lexeme, expr)
    
    def statement(self):
        if self.match(TokenType.IF):
            return self.ifStatement()
        
        if self.match(TokenType.WHILE):
            return self.whileStatement()
        
        if self.match(TokenType.PRINT):
            return self.printStatement()
        
        if self.match(TokenType.SELECT):
            return self.selectStatement()
        
        if self.match(TokenType.FOREACH):
            return self.foreachStatement
        
        return self.expressionStatement()
    
    def declaration(self):
        if (self.match(TokenType.CHAR, TokenType.DATE, TokenType.DAY, \
                       TokenType.INT, TokenType.REAL, TokenType.TIME)):
            type_token = self.previous()

            # Get the variable name
            name_token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

            # Consume the "="
            self.consume(TokenType.EQUAL, "Expect '=' in assignment.")

            # Parse the initializer expression
            value = self.expression()

            # Consume the ";"
            self.consume(TokenType.SEMICOLON, "Expect ';' in assignment.")

            return VarDecl(type_token.lexeme, name_token.lexeme, value)

        return self.statement()
    
    def program(self):
        statements = []
        while (not self.isAtEnd()):
            statements.append(self.declaration())

        return Program(statements)
    
    def match(self, *types: TokenType) -> bool:
        for type in types:
            if (self.check(type)):
                self.advance()
                return True
        return False
    
    def check(self, type: TokenType) -> bool:
        if (self.isAtEnd()):
            return False
        return self.peek().type == type

    def advance(self) -> Token:
        if (not self.isAtEnd()):
            self.current += 1
        return self.previous()
    
    def isAtEnd(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        
        # Just report error and return None
        self.transpiler.error(self.peek().line, message)
        return None