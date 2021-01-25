from enum import Enum, auto
from typing import NamedTuple, Any


class InstructionType(Enum):
    OP_RETURN = auto()
    OP_EXPR = auto()
    OP_JUMP = auto()
    OP_JUMP_FALSE = auto()
    GET_INPUT = auto()
    EXEC_LINE = auto()
    EXEC_CODE = auto()
    LABEL = auto()
    EXEC_GOTO = auto()
    EXEC_TAGS = auto()


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
    NAME = auto()
    COLON = auto()
    CONCAT = auto()
    SEMI = auto()
    PIPE = auto()
    DOT = auto()
    ID = auto()
    TEXT = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    END = auto()
    UNKNOWN = auto()
    EMPTY = auto()


class Token(NamedTuple):  # pylint: disable=inherit-non-class
    type: TokenType
    value: str = ''
    position: tuple[int, int] = (0, 0)


class Instruction(NamedTuple): # pylint: disable=inherit-non-class
    type: InstructionType
    args: tuple[Any, ...] = ()
