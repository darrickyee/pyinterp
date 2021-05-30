# %%
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional
from functools import singledispatchmethod


class DlgNode(ABC):
    def __init__(self, condition: str = '') -> None:
        self.condition = condition

    def is_valid(self, global_context: dict[str, Any] = None, local_context: Mapping[str, Any] = None) -> bool:
        return bool(eval(self.condition, global_context, local_context)) if self.condition else True

    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def __repr__(self) -> str:
        arglist = ('='.join((k, f"'{v}'" if isinstance(v, str) else str(v)))
                   for k, v in self.as_dict().items())

        return f'{self.__class__.__name__}({", ".join(arglist)})'


class DlgLabel(DlgNode):
    def __init__(self, label: str, *, condition: str = '') -> None:
        super().__init__(condition=condition)
        self.label = label

    def as_dict(self) -> dict[str, Any]:
        return {'label': self.label}


class DlgLine(DlgNode):

    def __init__(self,
                 speaker: str = '',
                 text: str = '',
                 speaker_tags: list[str] = None,
                 tags: list[str] = None,
                 *,
                 condition: str = '') -> None:
        super().__init__(condition=condition)

        self.speaker = speaker
        self.text = text
        self.speaker_tags = speaker_tags or []
        self.tags = tags or []

    def as_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in ('speaker', 'text', 'speaker_tags', 'tags')}


class DlgChoice(DlgNode):

    def __init__(self,
                 text: str = '[Continue]',
                 tags: list[str] = None,
                 target: str = '',
                 *,
                 condition: str = '') -> None:
        super().__init__(condition=condition)

        self.text = text
        self.tags = tags or []
        self.target = target

    def as_dict(self) -> dict[str, Any]:
        return {'text': self.text, 'target': self.target, 'tags': self.tags, 'valid': self.is_valid()}


class DlgChoices(DlgNode):

    def __init__(self, choices: list[DlgChoice]) -> None:
        super().__init__(condition='')
        self.choices = choices

    def as_dict(self) -> dict[str, Any]:
        return {'choices': [choice.as_dict() for choice in self.choices]}

    def __repr__(self) -> str:
        return f'DlgChoices({str(self.choices)})'

# %%


class DlgPlayer:

    def __init__(self, nodes: list[DlgNode] = None) -> None:
        self.nodes = nodes or []
        self._index = 0
        self._node: Optional[DlgNode] = None

    def current_node(self):
        if self._index < len(self.nodes):
            return self.nodes[self._index]

        return None

    def play(self, start=0):
        self._index = start
        while self.current_node():
            self.exec_node(self.current_node())

    @singledispatchmethod
    def exec_node(self, node: Any):
        raise NotImplementedError

    @exec_node.register
    def exec_line(self, line: DlgLine):
        if line.is_valid():
            print(f'{line.speaker}: {line.text}')
            input()

        self._index += 1

    @exec_node.register
    def exec_choices(self, choices: DlgChoices):
        clist = choices.choices
        if clist:
            for i, choice in enumerate(clist):
                print(f'{i+1}. {choice.text}')

            while True:
                c = input('Choose: ')
                if c and c.isnumeric() and 1 <= int(c) <= len(clist):
                    break

            self._index = self._get_label_index(clist[int(c) - 1].target)
        else:
            self._index += 1

    @exec_node.register
    def exec_label(self, label: DlgLabel):
        self._index += 1

        if not label.is_valid():
            while self.current_node() and not (
                isinstance(self.current_node(),
                           DlgLabel) and self.current_node().is_valid()
            ):
                self._index += 1

    def _get_label_index(self, label: str):
        if not label:
            return self._index + 1

        try:
            return next(i for i, v in enumerate(self.nodes) if isinstance(v, DlgLabel) and v.label == label)
        except StopIteration:
            return len(self.nodes)

# %%


lbl1 = DlgLabel('Start')
lbl2 = DlgLabel('Continue')
line1 = DlgLine('Bob', 'Hello!')
line2 = DlgLine('Bob', 'Goodbye.')
line3 = DlgLine('Me', 'Ok then bye.')
c1 = DlgChoice('Restart', target='Start')
c2 = DlgChoice('Continue')
cs1 = DlgChoices([c1, c2])

p = DlgPlayer([lbl1, line1, cs1, line2, lbl2, line3])

# %%
