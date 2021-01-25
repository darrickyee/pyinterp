# %%
from typing import cast
from functools import singledispatchmethod
import astnodes as N


class DlgData(dict):

    def __init__(self, label: str = '', text: str = '', tags: list[str] = None, valid=True):
        super().__init__(
            [('label', label), ('text', text), ('tags', tags or []), ('valid', valid)])

    @property
    def label(self) -> str:
        return self['label']

    @label.setter
    def label(self, value: str):
        self['label'] = value

    @property
    def text(self) -> str:
        return self['text']

    @text.setter
    def text(self, value: str):
        self['text'] = value

    @property
    def tags(self) -> list[str]:
        return self['tags']

    @tags.setter
    def tags(self, value: list[str]):
        self['tags'] = value

    @property
    def valid(self) -> bool:
        return self['valid']

    @valid.setter
    def valid(self, value: bool):
        self['valid'] = value


class Interpreter:

    def __init__(self, root) -> None:
        self.node = root
        self.locals = {}
        self.dialog: DlgData = DlgData()
        self.options: list[N.OptionNode] = []

        self.stack: list[N.AstNode] = [root]
        self.wait = False

    def run(self):
        self.stack = [self.node]
        self.execute(self.stack.pop(0))

    def _init_nodes(self):
        pass

    def execute(self, node: N.AstNode):
        print(self.stack)
        if self._evaluate(node.condition):
            self._execute(node)

    def next(self, idx=-1):
        if self.options:
            if 0 <= idx < len(self.options):
                self.stack = self.options[idx].children + self.stack
                self.options.clear()
            else:
                return

        self.wait = False
        if self.stack:
            self.execute(self.stack.pop(0))

    def _evaluate(self, expr: str):
        result = ''
        try:
            result = eval(expr, None, self.locals)
        except SyntaxError:
            pass

        return result

    @property
    def optionsview(self):
        view = list()
        for option in self.options:
            view.append(DlgData(
                '',
                option.text,
                option.tags,
                self._evaluate(option.condition)
            ))
        return view

    @singledispatchmethod
    def _execute(self, node):
        raise NotImplementedError

    @_execute.register
    def _execute_code(self, node: N.CodeNode):
        exec(node.code, None, self.locals)

    @_execute.register
    def _execute_optiongroup(self, node: N.OptionGroup):
        for option in node.children:
            self.options.append(cast(N.OptionNode, option))

        for i, option in enumerate(self.optionsview):
            print(f'{i+1}. {option.text} [{option.valid}]')

    @_execute.register
    def _execute_line(self, node: N.LineNode):
        self.wait = True
        self.dialog.label = self._evaluate(node.speaker)
        self.dialog.text = self._evaluate(node.text)
        self.dialog.tags = [self._evaluate(f'f"{tag}"') for tag in node.tags]
        print(f'{self.dialog.label}: {self.dialog.text}')

    @_execute.register
    def _execute_block(self, node: N.BlockNode):
        self.stack = node.children + self.stack

        while self.stack and not self.wait:
            self.execute(self.stack.pop(0))


# %%
c1 = N.CodeNode('abc = 12')
c2 = N.CodeNode('abc -= 1')
l1 = N.LineNode('f"Guy{abc}"', 'f"Hello"')
o1 = N.OptionNode('Do thing 1')
o2 = N.OptionNode('Do thing 2')
opts = N.OptionGroup()
opts.add_child(o1)
opts.add_child(o2)
o1.add_child(c2)
o1.add_child(N.LineNode('f""', 'f"abc is {abc}"'))

l2 = N.LineNode('"Player"', '"Well it\'s over"')
b1 = N.BlockNode('start', [l1, opts, l2])
r = N.BlockNode('', [c1, b1])
l2.add_child(b1)

I = Interpreter(r)
# %%
I.run()
# %%
