# %%
import re
import tokenize
from tokens import TokenType, Token

T = TokenType

KEYWORDS = {
    'line ': T.LINE,
    'label ': T.LABEL,
    'goto ': T.GOTO,
    'option ': T.OPTION,
    'if ': T.IF,
    '->': T.GOTO,
    '-': T.LINE,
    '@': T.LABEL,
    '*': T.OPTION,
    ':': T.COLON,
    ';': T.SEMI,
    '|': T.PIPE,
    'map ': T.MAP,
    '.': T.DOT
}

RE = {
    'ID_START': re.compile(r'[_a-zA-Z]'),
    'ID': re.compile(r'^[_a-zA-Z][_a-zA-Z0-9]*'),
    'STRING': re.compile(r'^([\'"])(([^\1\\]|\\.)*?)\1'),
    'CODE_TOKEN': re.compile(r'^(code +|\$)'),
    'CODE_INLINE': re.compile(r' *(.*)'),
    'CODE_BLOCK': re.compile(r' *:$')
}


class Lexer:

    def __init__(self) -> None:
        self.indent: int = 0
        self.tokens: list[Token] = []
        self.lines: list[str] = []
        self.row: int = 0
        self.col: int = 0

    @property
    def currchar(self) -> str:
        try:
            return self.lines[self.row][self.col]
        except IndexError:
            return ''

    @property
    def currline(self) -> str:
        return self.lines[self.row] if self.row < len(self.lines) else ''

    def rtext(self, strip: bool = False) -> str:
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

        # Remove redundant newlines
        tokens = self.tokens.copy()
        self.tokens = []
        for i, token in enumerate(tokens):
            if i > 0 and token.tokentype == self.tokens[-1].tokentype == T.NEWLINE:
                continue
            self.tokens.append(token)

        return self.tokens

    def _next_token(self):

        # Beginning of new line
        if self.col == 0:
            # Skip empty lines
            if not self.currline.strip():
                self._advance(len(self.currline))
                return

            # Indent/dedent
            self._get_indent()

        # Keywords/statements
        if self.rtext().startswith(tuple(KEYWORDS)):
            self._get_keyword()
            return

        if self.rtext().startswith(('code ', '$')):
            self._get_code()
            return

        if re.search(RE['ID_START'], self.currchar):
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

    def _add_token(self, T: T, value: str = ''):
        self.tokens.append(Token(T, value, (self.row+1, self.col+1)))

    def _advance(self, steps=1):
        self.col += steps

        while self.col >= len(self.currline):
            self.col -= len(self.currline)
            self.row += 1
            self._add_token(T.NEWLINE)

            if self.row >= len(self.lines):
                return

    def _get_code(self):
        self._advance(re.search(RE['CODE_TOKEN'], self.rtext()).end())
        value = re.search(RE['CODE_INLINE'], self.rtext()).group(1)
        if value:
            self._add_token(T.CODE, value)
            self._advance(len(value))
            return

        

    def _get_indent(self):
        indent = re.search(r'^ *', self.currline).end()

        if indent != self.indent:
            self._add_token(T.INDENT
                            if indent > self.indent
                            else T.DEDENT)
            self.indent = indent

            self._advance(indent)

    def _get_keyword(self):
        for keyword, T in KEYWORDS.items():
            if self.rtext().startswith(keyword):
                self._add_token(T, keyword.strip())
                self._advance(len(keyword))
                return

    def _get_word(self):

        value = re.search(RE['ID'], self.rtext()).group()
        self._add_token(T.ID, value)
        self._advance(len(value))
        return

    def _get_string(self):
        match = re.search(RE['STRING'], self.rtext())
        if match:
            value = re.search(RE['STRING'], self.rtext(strip=True)).group()
            self._add_token(T.STRING, value[1:-1])
            self._advance(len(match.group()))
            return
        else:
            self.throw('Unmatched quote detected.')

    def _get_expr(self):
        units = self.rtext().split('}')
        lbrackets = units[0].count('{')

        if lbrackets < len(units):
            expr = '}'.join(units[:lbrackets]) + '}'
            self._add_token(T.EXPR, expr[1:-1].replace('\n', ' '))
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

def genlines(inp: str):
    lines = (s+'\n' for s in inp.split('\n'))
    return lambda: next(lines)

def tokenize_str(instr: str):
    lines = (s+'\n' for s in instr.split('\n'))
    return tokenize.generate_tokens(lambda: next(lines))
# %%
