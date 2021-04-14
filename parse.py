# %%
from tokens import TokenType as T, AstNodeType as N
from typing import Any, Type
from lexer import tokenize, Token


class ScriptParseError(Exception):

    pass


class AstNode:

    def __init__(self,
                 nodetype: N = N.INVALID,
                 value: Any = None,
                 children: list['AstNode'] = None,
                 ifexpr: str = 'True',
                 tags: list[str] = None) -> None:
        self.nodetype = nodetype
        self.ifexpr = ifexpr
        self.tags = tags or []
        self.value = value or []
        self.children = children or []

    def emit(self):
        return []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(nodetype={self.nodetype}, value={self.value}, ifexpr={self.ifexpr})"


class BlockNode(AstNode):

    def __init__(self, head: AstNode, children: list[AstNode] = None) -> None:
        super().__init__(N.BLOCK, head, ifexpr=head.ifexpr, children=children)

        # script : block END
        # block : statement+
        # statement : head (IF EXPR)? suite?
        # suite: COLON NEWLINE INDENT statement+
        # head: (simple_stmt | stmt_head) tags?
        # tags: LBRACKET STRING+ RBRACKET
        # %%


class Parser:

    def __init__(self) -> None:
        self.tokens: list[Token] = list()
        self.position = 0

    @property
    def currtoken(self) -> Token:
        if self.position < len(self.tokens):
            return self.tokens[self.position]

        return Token(T.END)

    @property
    def M(self):
        return {
            T.LABEL: self._label,
            T.LINE: self._line,
            T.GOTO: self._goto,
            T.CHOICE: self._choice
        }

    def parse(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0
        while self.position < len(self.tokens) and self.currtoken.type != T.END:
            node = self._statement()
            yield node

        return

    def consume(self, tokentype: T, *others: T):
        if self.currtoken.type not in (tokentype, *others):
            raise ScriptParseError(
                f"Invalid syntax at line {self.currtoken.position[0]} ({self.currtoken.position[1]}): '{self.currtoken.value}'; expected {(tokentype, *others)}, got {self.currtoken.type}")

        token = self.currtoken
        self.position += 1
        return token

    def _matches(self, *args):
        args = ({arg} if isinstance(arg, str) else arg
                for arg in args)
        try:
            return all(self.tokens[self.position+i].type in arg
                       for i, arg in enumerate(args))
        except IndexError:
            return False

    def _statement(self):
        node = self._simple_stmt()

        if self.currtoken.type in (T.COLON, T.CONCAT):
            node.children = self._suite()
        else:
            self.consume(T.NEWLINE, T.END)

        return node

    def _simple_stmt(self):
        node = self._head()

        if self.currtoken.type == T.LBRACKET:
            self.consume(T.LBRACKET)
            while self.currtoken.type != T.RBRACKET:
                node.tags.append(self.consume(T.STRING).value)

            self.consume(T.RBRACKET)

        if self.currtoken.type == T.IF:
            self.consume(T.IF)
            node.ifexpr = self.consume(T.EXPR).value

        return node

    def _head(self) -> AstNode:
        node = AstNode(N.END)
        if fn := self.M.get(self.currtoken.type, None):
            node = fn()
        elif (tt := self.currtoken.type) in (T.STRING, T.NAME, T.EXPR):
            node = AstNode(N.TAIL, [self.consume(tt).value])
        else:
            self.consume(T.END)

        return node

    def _label(self):
        self.consume(T.LABEL)
        return AstNode(N.LABEL, [self.consume(T.NAME).value])

    def _line(self):
        self.consume(T.LINE)
        args = [self.consume(T.STRING, T.NAME, T.EXPR).value]

        if self.currtoken.type in (T.STRING, T.NAME, T.EXPR):
            args.append(self.consume(T.STRING, T.NAME, T.EXPR).value)

        return AstNode(N.LINE, args)

    def _goto(self):
        self.consume(T.GOTO)
        arg = None

        if self.currtoken.type in (T.STRING, T.NAME, T.EXPR):
            arg = [self.consume(T.STRING, T.NAME, T.EXPR).value]

        return AstNode(N.GOTO, arg)

    def _choice(self):
        self.consume(T.CHOICE)
        arg = None
        if self.currtoken.type in (T.STRING, T.NAME, T.EXPR):
            arg = [self.consume(T.STRING, T.NAME, T.EXPR).value]
        return AstNode(N.CHOICE, arg)

    def _tags(self):
        self.consume(T.LBRACKET)
        values = []
        while self.currtoken.type != T.RBRACKET:
            values.append(self.currtoken.value)
            self.consume(T.STRING)

        self.consume(T.RBRACKET)

        return AstNode(N.TAGS, values)

    def _suite(self):
        nodes = []
        if self.currtoken.type == T.COLON:
            self.consume(T.COLON)
            self.consume(T.NEWLINE)
            self.consume(T.INDENT)

            while self.currtoken.type != T.DEDENT:
                nodes.append(self._statement())

            self.consume(T.DEDENT)
        else:
            while self.currtoken.type != T.NEWLINE:
                self.consume(T.CONCAT)
                nodes.append(self._simple_stmt())
            self.consume(T.NEWLINE)

        return nodes


# %%
tkns = list(tokenize(open('TestDS.zds', 'r')))
# %%
p = Parser()
g = p.parse(tkns)
n = list(g)

# %%


def resolve(node: AstNode):
    if not (node.children and any(child.nodetype == N.TAIL
                                  for child in node.children)):
        return [node]

    nodes = []
    for child in node.children:
        if child.nodetype == N.TAIL:
            child.nodetype = node.nodetype
            child.ifexpr = 'True' if node.ifexpr == child.ifexpr == 'True' else node.ifexpr + \
                ' and ' + child.ifexpr
            child.value = node.value + child.value
            child.tags = node.tags + child.tags

            nodes.append(child)
        else:
            raise TypeError(f'node {node}: Invalid completion type')

    return nodes


def expand(nodes: list[AstNode]):
    nodelist = []
    for node in nodes:
        nodelist.extend(resolve(node))

    for node in nodelist:
        node.children = expand(node.children)

    return nodelist

    # %%
