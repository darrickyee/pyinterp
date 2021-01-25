# %%
from typing import Any
from lexer import tokenize, Token


class ScriptParseError(Exception):

    pass


# %%


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
        while self.position < len(self.tokens):
            node = self._label() if self.currtoken.type == 'LABEL' else self._goto()
            yield node

        return

    def consume(self, tokentype: str):
        if self.currtoken.type != tokentype:
            raise ScriptParseError(
                f"Invalid syntax at line {self.currtoken.position[0]} ({self.currtoken.position[1]}): '{self.currtoken.value}'")

        self.position += 1

    def _matches(self, *args):
        args = ({arg} if isinstance(arg, str) else arg
                for arg in args)
        try:
            return all(self.tokens[self.position+i].type in arg
                       for i, arg in enumerate(args))
        except IndexError:
            return False

    def _goto(self):
        node_args: dict[str, Any] = {'token': self.currtoken}
        self.consume('GOTO')
        node_args['label'] = self.currtoken.value
        self.consume('NAME')
        node = GotoNode(**node_args, **self._get_tail())
        self.consume('NEWLINE')
        return node

    def _label(self):
        node_args: dict[str, Any] = {'token': self.currtoken}
        self.consume('LABEL')
        node_args['label'] = self.currtoken.value if self.currtoken.type == 'NAME' else ''
        self.consume('NAME')
        node = LabelNode(**node_args, **self._get_tail())
        self.consume('NEWLINE')
        return node

    def _get_tail(self):
        return {'condition': self._ifclause(),
                'tags': self._tags()}

    def _ifclause(self):
        condition = 'True'
        if self._matches('IF'):
            self.consume('IF')
            condition = self.currtoken.value
            self.consume('EXPR')

        return condition

    def _tags(self):
        tags = list()
        if self._matches('LBRACKET'):
            self.consume('LBRACKET')
            while self.currtoken.type != 'RBRACKET':
                if self.currtoken.type == 'STRING':
                    tags.append(self.currtoken.value)

                self.consume('STRING')
            self.consume('RBRACKET')

        return tags


# %%
p = Parser()
g = p.parse(tkns)
# %%
