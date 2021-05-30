# %%
from typing import NamedTuple
from enum import Enum, auto
from typing import Any, Sequence


class InstructionType(Enum):

    SECTION = auto()
    LINE = auto()
    CHOICES = auto()
    GOTO = auto()
    SCRIPT = auto()
    JUMP_IF_FALSE = auto()
    SET_LOCAL = auto()
    END = auto()


I = InstructionType




class Instruction(NamedTuple):
    instruction_type: InstructionType
    args: Sequence

    # def __init__(self, instruction_type: InstructionType, args: Sequence = None) -> None:
    #     self.instruction_type = instruction_type
    #     self.args = args


class DlgPlayer:

    def __init__(self, instructions: Sequence[Instruction], context: dict[str, Any] = None) -> None:
        self.instructions = instructions
        self.context = context or dict()

        self.index = 0
        self.scope: list[str] = []
        self.sections: dict[str, int] = {instr.args[0]: i
                                         for i, instr in enumerate(self.instructions)
                                         if instr.instruction_type == I.SECTION}

        self.cmds = {
            I.SECTION: self.section,
            I.LINE: self.line,
            I.JUMP_IF_FALSE: self.jump_if_false,
            I.SET_LOCAL: self.set_local,
            I.GOTO: self.goto,
            I.SCRIPT: self.script,
            I.END: self.end
        }

    def play(self, start=0):
        self.index = start

        while self.index < len(self.instructions):
            instr = self.instructions[self.index]

            self.cmds[instr.instruction_type](instr.args)

        print('END')

    def jump_if_false(self, args: tuple[str, int]):
        condition, i = args
        self.index += 1 if eval(condition, self.context) else i+1

    def line(self, args: tuple[str, str]):
        speaker = eval(f'{args[0]}', self.context)
        text = eval(f'f{args[1]}', self.context)
        print(f'{speaker}: {text}')
        if input('') == 'EXIT':
            self.end()
        self.index += 1

    def section(self, args: tuple[str]):
        self.scope = args[0].split('.')
        self.index += 1

    def set_local(self, args: tuple[str, str]):
        self.context[args[0]] = eval(args[1], globals(), self.context)
        self.index += 1

    def goto(self, args: tuple[str]):
        self.index = self.sections.get(args[0], len(self.instructions))

    def script(self, args: tuple[str]):
        exec(args[0], globals(), self.context)
        self.index += 1

    def end(self, _=None):
        self.index = len(self.instructions)

# %%


instr_list = [
    Instruction(I.SECTION, ['Bob']),
    Instruction(I.SECTION, ('START',)),
    Instruction(I.LINE, ('"Bob"', '"Hello."')),
    Instruction(I.JUMP_IF_FALSE, ('met_player', 1)),
    Instruction(I.LINE, ('"Bob"', '"Good to see you, {player}."')),
    Instruction(I.JUMP_IF_FALSE, ('not met_player', 2)),
    Instruction(I.LINE, ('"Bob"', '"What\'s your name?"')),
    Instruction(I.LINE, ('player', '"{player}."')),
    Instruction(I.SCRIPT, ('met_player = True',)),
    Instruction(I.LINE, ('"Bob"', '"What can I do for you?"')),
    Instruction(I.SCRIPT, ('times += 1',)),
    Instruction(I.SCRIPT, ('print(f"Restarting (rep: {times})")',)),
    Instruction(I.GOTO, ('START', ))
]
# %%
p = DlgPlayer(instr_list, {'player': 'Bill', 'times': 0, 'met_player': False})
p.play()
# %%

def getstuff(a):
    return a / 3

def myfunc():

    if x == 2:
        print('OK')
        return x
    else:
        y = getstuff(4)
        return
# %%
