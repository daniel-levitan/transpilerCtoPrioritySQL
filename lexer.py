from token_type import TokenType, Token
from transpiler import Transpiler

class Lexer:
    KEYWORDS = {
        "and"   : TokenType.AND,
        "char"  : TokenType.CHAR,
        "date"  : TokenType.DATE,
        "day"   : TokenType.DAY,
        "else"  : TokenType.ELSE,
        "false" : TokenType.FALSE,
        "foreach" : TokenType.FOREACH,
        "from"  : TokenType.FROM,
        "if"    : TokenType.IF,
        "in"    : TokenType.IN,
        "int"   : TokenType.INT,
        "not"   : TokenType.NOT,
        "or"    : TokenType.OR,
        "print" : TokenType.PRINT,
        "real"  : TokenType.REAL,
        "select": TokenType.SELECT,
        "time"  : TokenType.TIME,
        "true"  : TokenType.TRUE,
        "where" : TokenType.WHERE,
        "while" : TokenType.WHILE,
    }

    def __init__(self, source: str, transpiler: Transpiler) -> None:
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.transpiler = transpiler

    # def lexerize(self) -> list:
    #     # placeholder lexing logic

    #     tokens = self.source
    #     return tokens
    
    # def scanTokens(self) -> list:
    def lexerize(self) -> list:
        while (not self.isAtEnd()):
            self.start = self.current
            self.scanToken()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scanToken(self) -> None:
        c = self.advance()
        match c:
            case '(':
                self.addToken(TokenType.LEFT_PAREN)
            case ')':
                self.addToken(TokenType.RIGHT_PAREN)
            case '{':
                self.addToken(TokenType.LEFT_BRACE)
            case '}':
                self.addToken(TokenType.RIGHT_BRACE)
            case ':':
                self.addToken(TokenType.COLON)
            case ',':
                self.addToken(TokenType.COMMA)
            case '-':
                self.addToken(TokenType.MINUS)
            case '%':
                self.addToken(TokenType.PERCENT)
            case '+':
                self.addToken(TokenType.PLUS)
            case '?':
                self.addToken(TokenType.QUESTION)
            case ';':
                self.addToken(TokenType.SEMICOLON)
            case '*':
                self.addToken(TokenType.STAR)
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if (self.match('/')):
                    # A comment goes until the end of the line.
                    while (self.peek() != '\n' and not self.isAtEnd()):
                        self.advance()
                else:
                    self.addToken(TokenType.SLASH)
            # case '&':
            #   if (self.peek() == '&'):
            #       self.addToken(TokenType.AND)
            #   else:

            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass

            case '\n':
                self.line += 1

            case '"':
                self.string('"')

            case "'":
                self.string("'")

            case _:
                if (self.isDigit(c)):
                    self.number()
                elif (self.isAlpha(c)):
                    self.identifier()
                else:
                    self.transpiler.error(self.line, "Unexpected character.")

    def isAtEnd(self) -> bool:
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]
    
    def addToken(self, type: TokenType) -> None:
        self.addToken(type, None)

    def addToken(self, type: TokenType, literal: object = None) -> None:
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def match(self, expected: str) -> bool:
        if self.isAtEnd():
            return False
        if self.source[self.current] != expected:
            return False 

        self.current += 1
        return True
    
    def peek(self) -> str:
        if (self.isAtEnd()):
            return '\0'
        return self.source[self.current]
    
    def string(self, quote_char) -> str:
        # Scan until we find the SAME quote
        while self.peek() != quote_char and not self.isAtEnd():
            # while (self.peek() != '"' and not self.isAtEnd()):
            if (self.peek() == '\n'):
                self.line += 1
            self.advance()

        if (self.isAtEnd()):
            self.transpiler.error(self.line, "Unterminated string.")
            return
        
        # The closing ".
        self.advance()

        # Trim the surrounding quotes.
        value = self.source[self.start + 1 : self.current - 1] 
        self.addToken(TokenType.STRING, value)

    def isDigit(self, c: str) -> bool:
        return c >= '0' and c <= '9'
    
    def peekNext(self):
        if (self.current + 1 >= len(self.source)):
            return '\0'
        return self.source[self.current + 1]
    
    def number(self):
        while (self.isDigit(self.peek())):
            self.advance()

        # Look for a fractional part.
        if (self.peek() == '.' and self.isDigit(self.peekNext())):
            self.advance()

        while (self.isDigit(self.peek())):
            self.advance()

        self.addToken(TokenType.NUMBER, float(self.source[self.start:self.current]))

    def isAlpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'
    
    def isAlphaNumeric(self, c: str) -> bool:
        return self.isAlpha(c) or self.isDigit(c)
    
    def identifier(self):
        while (self.isAlphaNumeric(self.peek())):
            self.advance()

        text = self.source[self.start:self.current]
        type = self.KEYWORDS.get(text)
        if (type == None):
            type = TokenType.IDENTIFIER

        self.addToken(type)