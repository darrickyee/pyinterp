# %%
from typing import NamedTuple
from functools import singledispatchmethod


class Option(NamedTuple):  # pylint: disable=inherit-non-class
    text: str
    condition: str = 'True'
    tags: list[str] = []


class Instruction:

    def __init__(self, condition: str = '', tags: list[str] = None) -> None:
        self.condition: str = condition or 'True'
        self.tags: list[str] = tags or []


class Line(Instruction):

    def __init__(self, speaker: str, text: str, condition: str = 'True') -> None:
        super().__init__(condition=condition)
        self.speaker = speaker
        self.text = text


class Options(Instruction):
    def __init__(self, options: list[Option]) -> None:
        super().__init__()
        self.options = options


class Label(Instruction):

    def __init__(self, label: str, condition: str = 'True', tags: list[str] = None) -> None:
        super().__init__(condition=condition, tags=tags)
        self.label = label


class Goto(Instruction):
    def __init__(self, label: str, condition: str = 'True', tags: list[str] = None) -> None:
        super().__init__(condition=condition, tags=tags)
        self.label = label


CMDS = [
    Label('Start'),
    Line('Bob', 'Hello.'),
    Line('Bob', 'How are you?', 'not hasmet'),
    Line('Bob', 'Good to see you, {player}!', 'hasmet'),
    Goto('Met', 'hasmet'),
    Line('Bob', 'What is your name?'),
    Line('Player', 'Bill.'),
    Label('Met'),
    Line('Bob', 'What can I do for you, {player}?')
]

# %%


class DlgPlayer:

    def __init__(self, instructions: list[Instruction] = None, context: dict = None) -> None:
        self.instructions = instructions or []
        self.context = context or {}
        self._index = 0

    def play(self):
        self._run(self.instructions[0])

    def select(self, option: int = -1):
        self._index += 1
        if self._index < len(self.instructions):
            self._run(self.instructions[self._index])

    @singledispatchmethod
    def _run(self, instruction):
        raise NotImplementedError

    @_run.register
    def _run_line(self, line: Line):
        if eval(line.condition, self.context):
            text = eval(f"f'{line.text}'", self.context)
            print(f'{line.speaker}: {text}')
            input('Press enter to continue...')
        self.select()

    @_run.register
    def _run_goto(self, goto: Goto):
        if eval(goto.condition, self.context):
            idx = [instr.label if isinstance(
                instr, Label) else '' for instr in self.instructions].index(goto.label)
            self._index = idx - 1
        self.select()

    @_run.register
    def _run_label(self, instr: Label):
        self.select()


# %%
vars = {
    'hasmet': False,
    'player': 'Bill'
}
player = DlgPlayer(CMDS, vars)
# %%
