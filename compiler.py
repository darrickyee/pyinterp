# %%
from token import COLON
from tokens import InstructionType as IType, Instruction as I, TokenType as T, Token
from lexer import tokenize


# Order of ops:
# 1. Evaluate if
# 2. Send tags
# 3. Execute statement
# 4. For each child in block:
#       4a. Do 1

class ScriptSyntaxError(SyntaxError):
    pass


STMT_ARGS = {
    T.LABEL: 1,
    T.LINE: 2,
    T.OPTION: 1,
    T.GOTO: 1
}


STMT_INSTR = {
    T.LINE: IType.EXEC_LINE,
    T.GOTO: IType.EXEC_GOTO,
    T.LABEL: IType.LABEL,
    T.OPTION: IType.EXEC_LINE
}

STMT_DEF = {
    T.LINE: ('_line', 2),
    T.GOTO: ('_goto', 1),
    T.LABEL: ('_label', 1),
    T.OPTION: ('_option', 1)
}


PREC = {
    T.LINE: 0,
    T.IF: 1,
    T.COLON: 2
}


class Compiler:

    def __init__(self) -> None:
        self.tokens: list[Token] = []
        self.position: int = 0
        self.instructions: list = []

    @property
    def currtoken(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def compile(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0
        self.instructions.clear()
        self._script()

    def consume(self, tokentype: T):
        if self.currtoken.type == tokentype:
            self.position += 1
            return

        self.error()

    def write(self, instruction_type: IType, *args):
        self.instructions.append((instruction_type, args))

    def instruction(self, instruction_type: IType, *args):
        return I(instruction_type, args)

    def error(self, msg: str = ''):
        row, col = self.currtoken.position
        raise ScriptSyntaxError(
            f"Line {row+1} ({col+1}), at '{self.currtoken.value}': {msg or 'Invalid syntax'} [{self.position}: {self.currtoken}]")

    # =========================

    def _script(self):
        while self.currtoken.type != T.END:
            if self.currtoken.type == T.NEWLINE:
                self.consume(T.NEWLINE)
                continue

            self.instructions.extend(self._statement())

    def _statement(self):
        chunk = self._simple_stmt()
        if self.currtoken.type == T.IF:
            self.consume(T.IF)

            cond = I(IType.OP_EXPR, (self.currtoken.value, ))
            self.consume(T.EXPR)

            chunk = chunk + self._suite()
            chunk = [cond, I(IType.OP_JUMP_FALSE, (len(chunk)+1, ))] + chunk
        else:
            self.consume(T.NEWLINE)

        print(chunk)
        return chunk

    def _compound_stmt(self):
        pass

    def _chunk(self):
        return [I(IType.EXEC_LINE)]

    def stmt(self, bp=0):
        left = self._chunk()
        while bp < self._bp(self.currtoken.type):
            left = self.stmt(PREC[self.currtoken.type]) + left

        return left

    def _bp(self, op: T):
        return PREC[op]

    def _led(self, left, op):
        return left + self.stmt(self._bp(op))

    def _suite(self):
        chunk = list()

        if self.currtoken.type == T.COLON:
            try:
                self.consume(T.COLON)
                self.consume(T.NEWLINE)
                self.consume(T.INDENT)
            except ScriptSyntaxError:
                self.error('Expected an indented block.')

            while self.currtoken.type != T.DEDENT:
                chunk.extend(self._statement())

            self.consume(T.DEDENT)

        elif self.currtoken.type == T.CONCAT:
            while self.currtoken.type != T.NEWLINE:
                self.consume(T.CONCAT)
                chunk.append(self._simple_stmt)

            self.consume(T.NEWLINE)

        elif self.currtoken.type == T.NEWLINE:
            self.consume(T.NEWLINE)

        return chunk

    def _simple_stmt(self):
        if (stmt := self.currtoken.type) in STMT_ARGS:
            self.consume(stmt)

            method, *_ = STMT_DEF[stmt]
            return getattr(self, method)()

        self.error('Unrecognized statement.')

    def _line(self):
        return [
            self._str_expr(),
            self._str_expr(),
            I(IType.EXEC_LINE)
        ]

    def _label(self):
        name = self.currtoken.value
        self.consume(T.NAME)
        self.instructions.append(I(IType.LABEL, (name,)))
        return []

    def _str_expr(self):
        toktype = self.currtoken.type
        tokvalue = self.currtoken.value

        if toktype in (T.EXPR, T.STRING, T.NAME):
            instr = self.instruction(
                IType.OP_EXPR, f'f{tokvalue}' if toktype == T.STRING else tokvalue)
            self.consume(toktype)
            return instr

        self.error('Expected an expression, name, or string.')

    def _stmt_tail(self):
        if self.currtoken.type == T.IF:
            self._ifclause()

        if self.currtoken.type == T.LBRACKET:
            self._tags()

        return

    def _ifclause(self):
        self.consume(T.IF)
        if not self.currtoken.type == T.EXPR:
            self.error('Expected an expression.')

        self.write(IType.OP_EXPR, self.currtoken.value)
        self.consume(T.EXPR)

        self.write(IType.OP_JUMP_FALSE, -1)
        jumpstart = len(self.instructions) - 1

        if self.currtoken.type == T.LBRACKET:
            self._tags()

        if self.currtoken.type in (T.CONCAT, T.COLON):
            self.consume(T.COLON)
            self._suite()
        else:
            self.consume(T.NEWLINE)

        offset = len(self.instructions) - jumpstart
        self.instructions[jumpstart] = (IType.OP_JUMP_FALSE, offset)

    def _tags(self):
        self.consume(T.LBRACKET)
        tags = []
        while self.currtoken.type != T.RBRACKET:
            self._str_expr()

        self.consume(T.RBRACKET)
        self.write(IType.EXEC_TAGS, tuple(tags))


# %%
c = Compiler()
tkns = list(tokenize(open('TestDS.zds', 'r')))
# %%
try:
    c.compile(tkns)
finally:
    c.instructions
# %%
