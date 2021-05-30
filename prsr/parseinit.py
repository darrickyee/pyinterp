import ast


def flatten(obj):

    if not isinstance(obj, list):
        return [obj]

    if not obj:
        return obj

    return flatten(obj[0]) + flatten(obj[1:])


def str_val(x):
    return f'"{x}"' if isinstance(x, str) else f'{x}'


def get_str(s):
    return eval(s.string, {}) if s.type == 3 else s.string


class Statement(ast.AST):

    PROPS = ('body')

    def __init__(self, body=None):
        self.body = body or []

    def __repr__(self):
        props = (f'{k}={str_val(getattr(self, k))}' for k in self.PROPS)
        return f'{self.__class__.__name__}({", ".join(props)})'


class Section(Statement):

    PROPS = ('label', 'body')

    def __init__(self, label, body):
        super().__init__(body=body)
        self.label = label


class Line(Statement):

    PROPS = ('text', 'body')

    def __init__(self, text, body):
        super().__init__(body=body)
        self.text = text


class Choice(Statement):

    PROPS = ('text', 'body')

    def __init__(self, text, body):
        super().__init__(body=body)
        self.text = text


class Cond(Statement):

    PROPS = ('code', 'body')

    def __init__(self, code, body=None):
        super().__init__(body=body)
        self.code = code


class Goto(Statement):

    PROPS = ('label',)

    def __init__(self, label):
        super().__init__(body=None)
        self.label = label


class PyExec(Statement):

    PROPS = ('code')

    def __init__(self, code):
        super().__init__(body=None)
        self.code = code


class PyExpr(ast.AST):

    def __init__(self, code: str) -> None:
        self.code = code

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(code={self.code})'
