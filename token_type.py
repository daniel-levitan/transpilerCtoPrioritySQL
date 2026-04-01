from enum import Enum, auto

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()    # (
    RIGHT_PAREN = auto()   # )
    LEFT_BRACE = auto()    # {
    RIGHT_BRACE = auto()   # }
    COLON = auto()         # :
    COMMA = auto()         # ,
    MINUS = auto()         # -
    PERCENT = auto()       # %
    PLUS = auto()          # +
    QUESTION = auto()      # ?
    SEMICOLON = auto()     # ;
    SLASH = auto()         # /
    STAR = auto()          # *

    # One or two character tokens
    BANG = auto()          # !
    BANG_EQUAL = auto()    # !=
    EQUAL = auto()         # =
    EQUAL_EQUAL = auto()   # ==
    GREATER = auto()       # >
    GREATER_EQUAL = auto() # >=
    LESS = auto()          # <
    LESS_EQUAL = auto()    # <=

    # Literals
    IDENTIFIER = auto()    # varible names
    STRING = auto()        # 'text''
    NUMBER = auto()        # 123 or 123.456

    # Keywords
    AND = auto()           # AND
    CHAR = auto()          # char
    DATE = auto()          # date
    DAY = auto()           # day
    ELSE = auto()          # else
    FOREACH = auto()       # foreach
    FALSE = auto()         # false
    FROM = auto()          # from
    IF = auto()            # if
    IN = auto()            # in
    INT = auto()           # int
    NOT = auto()           # NOT
    OR = auto()            # OR
    PRINT = auto()         # print
    REAL = auto()          # real
    SELECT = auto()        # select
    TIME = auto()          # time
    TRUE = auto()          # true
    WHERE = auto()         # where
    WHILE = auto()         # while

    EOF = auto()           # end of file


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: object, line: int) -> None:
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self) -> str:
        return f"{self.type} {self.lexeme} {self.literal}"
    
    def __repr__(self) -> str:
        return self.__str__()