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
    T.CHOICE: 1,
    T.GOTO: 1
}


STMT_INSTR = {
    T.LINE: IType.EXEC_LINE,
    T.GOTO: IType.EXEC_GOTO,
    T.LABEL: IType.LABEL,
    T.CHOICE: IType.EXEC_LINE
}

STMT_DEF = {
    T.LINE: ('_line', 2),
    T.GOTO: ('_goto', 1),
    T.LABEL: ('_label', 1),
    T.CHOICE: ('_option', 1)
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

    def consume(self, tokentype: T, *others: T):
        # print(f'Token: {self.currtoken}')
        if self.currtoken.type in [tokentype, *others]:
            tk = self.currtoken
            self.position += 1
            return tk

        self.error()

    def write(self, instruction_type: IType, *args):
        self.instructions.append((instruction_type, args))

    def instruction(self, instruction_type: IType, *args):
        return I(instruction_type, args)

    def error(self, msg: str = ''):
        row, col = self.currtoken.position
        raise ScriptSyntaxError(
            f"Line {row} ({col}), at '{self.currtoken.value}': {msg or 'Invalid syntax'} [{self.position}: {self.currtoken}]")

    # =========================

    def _script(self):
        while self.currtoken.type != T.END:
            if self.currtoken.type == T.NEWLINE:
                self.consume(T.NEWLINE)
                continue

            self.instructions.extend(self._statement())

    def _statement(self):

        if self.currtoken.type == T.CHOICE:
            return self._option()

        chunk = self._simple_stmt()

        for fn in self._tags, self._ifclause:
            if self.currtoken.type == T.NEWLINE:
                self.consume(T.NEWLINE)
                return chunk

            chunk = fn(chunk)

        return chunk

    def _compound_stmt(self):
        pass

    def _chunk(self):
        return [I(IType.EXEC_LINE)]

    def _suite(self, left=None):
        left = left or []
        chunk = []

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
            while self.currtoken.type == T.CONCAT:
                self.consume(T.CONCAT)
                chunk.extend(self._simple_stmt())
                chunk.extend(self._tags())
                chunk.extend(self._ifclause())

            self.consume(T.NEWLINE)

        elif self.currtoken.type == T.NEWLINE:
            self.consume(T.NEWLINE)

        return chunk

    def _head(self):
        

    def _simple_stmt(self):
        if (stmt := self.currtoken.type) in STMT_ARGS:
            method, *_ = STMT_DEF[stmt]
            return getattr(self, method)()

        self.error('Unrecognized statement.')

    def _line(self):
        self.consume(T.LINE)
        spkr = self.consume(T.STRING, T.NAME, T.EXPR).value
        text = self.consume(T.STRING, T.NAME, T.EXPR).value

        return [I(IType.EXEC_LINE, (spkr, text))]

    def _label(self):
        self.consume(T.LABEL)
        name = self.currtoken.value
        self.consume(T.NAME)
        self.instructions.append(I(IType.LABEL, (name,)))
        return []

    def _option(self):
        arglists = []
        suites = []
        while self.currtoken.type == T.CHOICE:
            self.consume(T.CHOICE)
            args = []
            args.append(self.consume(T.STRING, T.NAME, T.EXPR).value)

            tags = self._tags()

            if self.currtoken.type == T.IF:
                self.consume(T.IF)
                args.append(self.consume(T.EXPR).value)
            else:
                args.append('True')

            arglists.append(args)

            suites.append(tags + self._suite() + ['TEMP_JUMP'])

        out = []
        for i, arglist in enumerate(arglists):
            arglist.append(1 +
                           sum(len(suite) for suite in suites[:i]))
            out.append(I(IType.ADD_OPTION, tuple(arglist)))

        out.append(I(IType.EXEC_OPTIONS))
        total = sum(len(suite) for suite in suites) + len(out)
        for suite in suites:
            suite[-1] = I(IType.OP_JUMP, (
                total - len(out) - len(suite) + 1, )
            )
            out.extend(suite)

        return out

    def _ifclause(self, left=None):
        left = left or []
        out = left
        if self.currtoken.type == T.IF:
            self.consume(T.IF)
            if not self.currtoken.type == T.EXPR:
                self.error('Expected an expression.')

            expr = self.consume(T.EXPR).value
            suite = self._suite()

            out = [I(IType.OP_JUMP_FALSE, (expr, len(
                left) + len(suite) + 1))] + left + suite

        return out

    def _tags(self, left=None):
        left = left or []
        out = []
        if self.currtoken.type == T.LBRACKET:
            self.consume(T.LBRACKET)
            tags = []
            while self.currtoken.type != T.RBRACKET:
                tags.append(self.consume(T.STRING).value)

            self.consume(T.RBRACKET)
            out.append(I(IType.EXEC_TAGS, tuple(tags)))

        return left + out


# %%
c = Compiler()
tkns = list(tokenize(open('TestDS.zds', 'r')))
c.compile(tkns)
# %%
try:
    c.compile(tkns)
finally:
    c.instructions

# %%
# line_stmt NEWLINE => exec_line
# line_stmt tags NEWLINE => exec_tags exec_line
# line_stmt ifclause NEWLINE => jumpif exec_line
# line_stmt tags ifclause NEWLINE => jumpif exec_tags exec_line

# line_stmt COLON stmt1 stmt2 DEDENT => exec_line stmt1 stmt2
# line_stmt tags COLON stmt1 stmt2 DEDENT => tags exec_line stmt1 stmt2
# line_stmt ifclause COLON stmt1 stmt2 DEDENT => ifclause exec_line stmt1 stmt2

# option tags if COLON block => option(ifexpr, jump) (jumptgt)-> tags block
