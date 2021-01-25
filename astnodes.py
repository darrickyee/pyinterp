

class AstNode:

    def __init__(self, condition: str = '', tags: list[str] = None) -> None:
        self.condition = condition or 'True'
        self.tags = tags or []
        self.children: list['AstNode'] = []

    def add_child(self, node: 'AstNode'):
        self.children.append(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(condition={self.condition}, tags={self.tags})"


class CodeNode(AstNode):

    def __init__(self, code: str, condition: str = '', tags: list[str] = None) -> None:
        super().__init__(condition=condition, tags=tags)
        self.code = code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code})"


class BlockNode(AstNode):

    def __init__(self, label: str, children: list[AstNode] = None, condition: str = '', tags: list[str] = None) -> None:
        super().__init__(condition=condition, tags=tags)
        self.label = label
        self.children = children or []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(children={self.children})"


class OptionGroup(AstNode):
    pass


class OptionNode(AstNode):

    def __init__(self, text: str, condition: str = '', tags: list[str] = None) -> None:
        super().__init__(condition, tags)
        self.text = text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(text={self.text})"


class LineNode(AstNode):

    def __init__(self, speaker: str, text: str, condition='', tags=None) -> None:
        super().__init__(condition, tags)
        self.speaker = speaker
        self.text = text

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(speaker={self.speaker}, text={self.text})"


class GotoNode(AstNode):
    def __init__(self, label: str, condition: str = '', tags: list[str] = None) -> None:
        super().__init__(condition, tags)
        self.label = label


class LabelNode(AstNode):

    def __init__(self, label: str, condition: str = '', tags: list[str] = None) -> None:
        super().__init__(condition, tags)
        self.label = label
