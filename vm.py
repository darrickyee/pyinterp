# %%
from tokens import InstructionType as IType, Instruction as I


# EXEC('player = MC')
# LABEL('Start')
# EXPR('met == False')
# OP_JUMP_IF_FALSE(14)
# EXEC('met = True')
# LINE(npc1, 'HIT.  What\'s your name?')
# EXPR('shy == True')
# OP_JUMP_IF_FALSE(4)
# TAGS('shy')
# LINE(player, "I'd rather not say.")
# WAIT
# EXPR('shy == False')
# OP_JUMP_IF_FALSE(4)
# TAGS('bold')
# LINE(player, '{player}')
# WAIT
# LINE(npc1, 'Nice to meet you, {player}!')
# LINE(npc1, 'What class do you want to be?')

# OP_EXPR(expr) -> Push value
# OP_JUMP_FALSE(offset) -> ip += 1 if values.pop() else offset
# EXEC_LINE

# PUSH_OPTION(text, valid, jump_target)
# PUSH_OPTION(text, valid, jump_target)
# PUSH_OPTION(text, valid, jump_target)
# END_OPTIONS
# GET_INPUT
# EXPR('0 <= input < len(Options)')
# OP_JUMP_IF_FALSE(-2)
# EXPR('Options[input])

# %%

METHODS = {
    IType.OP_JUMP_FALSE: 'jump_if_false',
    IType.OP_EXPR: 'expr',
    IType.GET_INPUT: 'get_input',
    IType.EXEC_LINE: 'line',
    IType.EXEC_CODE: 'code',
    IType.EXEC_GOTO: 'goto'
}


class VM:

    def __init__(self) -> None:
        self.chunk: list[tuple[I, tuple]] = list()
        self._ip: int = 0
        self._lastip: int = -1
        self.valuestack: list = list()
        self.inputstack: list = list()

        self.locals = dict()

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, value):
        self._ip = value

    def interpret(self, chunk: list):
        self.chunk = chunk
        self.ip = 0
        return self.run()

    def run(self):
        while self._lastip != self.ip and self.ip < len(self.chunk):
            self._lastip = self.ip
            instr = self.chunk[self.ip]
            # print(instr)
            if METHODS.get(instr[0], None):
                fn = getattr(self, METHODS[instr[0]])
                fn(*instr[1])

    def code(self, code_str):
        exec(code_str, None, self.locals)
        self.ip += 1

    def goto(self, label: str):
        idx = self.ip + 1
        try:
            idx = self.chunk.index((IType.BLOCK, (label, ))) + 1
        except ValueError:
            pass

        self.ip = idx

    def line(self):
        if self.inputstack:
            self.inputstack.pop()
        text = self.valuestack.pop()
        speaker = self.valuestack.pop()
        print(f'{speaker}: {text}')

    def expr(self, expr_str):
        self.valuestack.append(eval(expr_str, None, self.locals))
        self.ip += 1

    def jump_if_false(self, offset=1):
        if self.valuestack.pop():
            self.ip += 1
        else:
            self.ip += offset

    def send_input(self, idx=-1):
        self.inputstack.append(idx)
        self.ip += 1
        self.run()


# %%
C = [
    (IType.EXEC_CODE, ('met = True',)),
    (IType.OP_EXPR, ('"Bob"',)),
    (IType.OP_EXPR, ('"Hello"',)),
    (IType.EXEC_LINE, ()),
    (IType.EXEC_GOTO, ('mylabel', )),
    (IType.OP_EXPR, ('"Bob"',)),
    (IType.OP_EXPR, ('"How are you?"',)),
    (IType.EXEC_LINE, ()),
    (IType.OP_EXPR, ('met',)),
    (IType.OP_JUMP_FALSE, (4, )),
    (IType.OP_EXPR, ('"Player"',)),
    (IType.OP_EXPR, ('"Shitty."',)),
    (IType.EXEC_LINE, ()),
    (IType.OP_EXPR, ('not met',)),
    (IType.OP_JUMP_FALSE, (5, )),
    (IType.BLOCK, ('mylabel', )),
    (IType.OP_EXPR, ('"Player"',)),
    (IType.OP_EXPR, ('"Not bad."',)),
    (IType.EXEC_LINE, ())
]
# %%
v = VM()
v.interpret(C)
# %%


# if_clause: OP_EXPR(expr) JUMP_IF_FALSE(offset)
# tags: EXEC_TAGS(taglist)
# line: OP_EXPR(speaker) OP_EXPR(text) EXEC_LINE()
# goto: EXEC_GOTO(label)
# label: LABEL(label)
