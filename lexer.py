# %%
import re
from tokens import TokenType, Token


class Lexer:

    WORDS = {
        'line ': TokenType.LINE,
        'label ': TokenType.LABEL,
        'goto ': TokenType.GOTO,
        'option ': TokenType.OPTION,
        'code ': TokenType.CODE,
        'if ': TokenType.IF,
        '->': TokenType.GOTO,
        '-': TokenType.LINE,
        '@': TokenType.LABEL,
        '*': TokenType.OPTION,
        '$': TokenType.CODE,
        ':': TokenType.COLON,
        ';': TokenType.SEMI,
        '|': TokenType.PIPE,
        'map ': TokenType.MAP,
        '.': TokenType.DOT
    }

    def __init__(self) -> None:
        self.indent: int = 0
        self.tokens: list[Token] = []
        self.lines: list[str] = []
        self.row: int = 0
        self.col: int = 0

    @property
    def currchar(self):
        try:
            return self.lines[self.row][self.col]
        except IndexError:
            return ''

    @property
    def currline(self):
        return self.lines[self.row] if self.row < len(self.lines) else ''

    def rtext(self, strip=False):
        if strip:
            return self.currline[self.col:] + '\n' + '\n'.join(ln.lstrip(' ') for ln in self.lines[self.row + 1:])

        return self.currline[self.col:] + '\n' + '\n'.join(ln for ln in self.lines[self.row + 1:])

    def tokenize(self, instr: str) -> list[Token]:
        self.lines = instr.split('\n')

        self.row = 0
        self.col = 0
        self.tokens.clear()

        while self.row < len(self.lines):
            self._next_token()

        return self.tokens

    def _next_token(self):

        if self.col == 0:
            if not self.currline.strip():
                self._advance(len(self.currline))
                return
            self._get_indent()

        if self.rtext().startswith(tuple(self.WORDS)):
            self._get_word()
            return

        if re.search(r'[_a-zA-Z]', self.currchar):
            self._get_word()
            return

        if self.currchar in ('"', '\''):
            self._get_string()
            return

        if self.currchar == '{':
            self._get_expr()
            return

        if self.currchar == ' ':
            self._advance()
            return

        self.throw(f"Unexpected token: '{self.currchar}'.")

    def throw(self, message=''):
        raise ValueError(
            f"Line {self.row+1} ({self.col+1}): {message}"
        )

    def _add_token(self, tokentype: TokenType, value: str = ''):
        self.tokens.append(Token(tokentype, value, (self.row+1, self.col+1)))

    def _advance(self, steps=1):
        self.col += steps

        while self.col >= len(self.currline):
            self.col -= len(self.currline)
            self.row += 1
            self._add_token(TokenType.NEWLINE)

            if self.row >= len(self.lines):
                return

    def _get_indent(self):
        indent = re.search(r'^ *', self.currline).end()

        if indent != self.indent:
            self._add_token(TokenType.INDENT
                            if indent > self.indent
                            else TokenType.DEDENT)
            self.indent = indent

            self._advance(indent)

    def _get_word(self):
        for keyword, tokentype in self.WORDS.items():
            if self.rtext().startswith(keyword):
                self._add_token(tokentype, keyword.strip())
                self._advance(len(keyword))
                return

        value = re.search(r'^[_a-zA-Z]+[_a-zA-Z0-9]*', self.rtext()).group()
        self._add_token(TokenType.ID, value)
        self._advance(len(value))
        return

    def _get_string(self):
        match = re.search(r'^([\'"])(([^\1\\]|\\.)*?)\1', self.rtext())
        if match:
            value = re.search(
                r'^([\'"])(([^\1\\]|\\.)*?)\1', self.rtext(strip=True)).group()
            self._add_token(TokenType.STRING, value[1:-1])
            self._advance(len(match.group()))
            return
        else:
            self.throw('Unmatched quote detected.')

    def _get_expr(self):
        units = self.rtext().split('}')
        lbrackets = units[0].count('{')

        if lbrackets < len(units):
            expr = '}'.join(units[:lbrackets]) + '}'
            self._add_token(TokenType.EXPR, expr[1:-1].replace('\n', ' '))
            self._advance(len(expr))
            return

        self.throw('Unclosed expression detected.')


# %%
out = []
with open('test2.zds', 'r', encoding='utf-8') as f:
    out = f.read()

lx = Lexer()
lx.tokenize(out)
# %%

# %%
