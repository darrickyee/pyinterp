# %%
from abc import ABC, abstractmethod
from tokens import TokenType
from lexer import Token


class AstNode(ABC):

    def __init__(self, token: Token) -> None:
        self.token = token
        self.children: list['AstNode'] = []

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    def add_child(self, node: 'AstNode'):
        self.children.append(node)


class LineNode(AstNode):

    def execute(self):
        return


class LabelNode(AstNode):

    def execute(self):
        return


class IdNode(AstNode):

    def execute(self):
        return


class Parser:

    def __init__(self) -> None:
        self.tokens: list[Token] = list()
        self.position = 0

    @property
    def currtoken(self) -> Token:
        return self.tokens[self.position]

    def parse(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0
        return self._label()

    def consume(self, tokentype: TokenType):
        if self.currtoken.tokentype != tokentype:
            raise ValueError(
                f"Invalid syntax at line {self.currtoken.position[0]} ({self.currtoken.position[1]}): '{self.currtoken.value}'")

        self.position += 1

    def _label(self):
        node = LabelNode(self.currtoken)
        self.consume(TokenType.LABEL)
        node.add_child(IdNode(self.currtoken))
        self.consume(TokenType.ID)
        return node
