from enum import Enum, auto


class TokenType(Enum):
    LABEL = auto()
    GOTO = auto()
    LINE = auto()
    OPTION = auto()
    CODE = auto()
    MAP = auto()
    EXPR = auto()
    IF = auto()
    STRING = auto()
    COLON = auto()
    SEMI = auto()
    PIPE = auto()
    DOT = auto()
    ID = auto()
    TEXT = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()


class Token:

    def __init__(self, tokentype: TokenType, value: str = None, position: tuple[int, int] = None) -> None:
        self.tokentype = tokentype
        self.value = value
        self.position = position or tuple()

    def __repr__(self) -> str:
        return f'Token(tokentype={self.tokentype}, value="{self.value}", position={self.position})'

    def __str__(self) -> str:
        return self.__repr__()
