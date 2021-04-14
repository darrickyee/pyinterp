from enum import Enum, auto
from typing import NamedTuple, Any


class AstNodeType(Enum):
    LABEL = auto()
    GOTO = auto()
    LINE = auto()
    CHOICE = auto()
    CHOICES = auto()
    CODE = auto()
    MAP = auto()
    EXPR = auto()
    IF = auto()
    BLOCK = auto()
    TAGS = auto()
    INVALID = auto()
    END = auto()
    TAIL = auto()

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
    ADD_OPTION = auto()
    EXEC_OPTIONS = auto()


class TokenTypeOld(Enum):
    LABEL = auto()
    GOTO = auto()
    LINE = auto()
    CHOICE = auto()
    CODE = auto()
    MAP = auto()
    AS = auto()
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

class TokenType(Enum):
    CONSTANT = auto()
    OPERATOR = auto()
    STATEMENT = auto()
    NAME = auto()
    INDENT = auto()
    DEDENT = auto()
    NEWLINE = auto()
    END = auto()
    UNKNOWN = auto()

class Token(NamedTuple):  # pylint: disable=inherit-non-class
    type: TokenType
    value: str = ''
    position: tuple[int, int] = (0, 0)


class Instruction(NamedTuple): # pylint: disable=inherit-non-class
    type: InstructionType
    args: tuple[Any, ...] = ()
