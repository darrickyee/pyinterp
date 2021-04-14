# %%
from token import DEDENT, ENDMARKER, INDENT, NEWLINE, STRING
import tokenize as T
from functools import singledispatch
from io import TextIOBase
from typing import Generator, Iterable, Union
from tokens import Token, TokenType as TT
# %%

_BUILTINS: dict[tuple[int, str], str] = {
    (T.NAME, 'label'): 'LABEL',
    (T.OP, '@'): 'LABEL',
    (T.NAME, 'goto'): 'GOTO',
    (T.OP, '->'): 'GOTO',
    (T.NAME, 'line'): 'LINE',
    (T.OP, '-'): 'LINE',
    (T.NAME, 'choice'): 'CHOICE',
    (T.OP, '*'): 'CHOICE',
    (T.NAME, 'map'): 'MAP',
    (T.OP, '**'): 'MAP',
    (T.NAME, 'as'): 'AS',
    (T.OP, '{'): 'LBRACE',
    (T.OP, '}'): 'RBRACE',
    (T.NAME, 'code'): 'CODE',
    (T.ERRORTOKEN, '$'): 'CODE',
    (T.OP, '|'): 'CONCAT',
    (T.OP, ':'): 'COLON',
    (T.NAME, 'if'): 'IF',
    (T.OP, '['): 'LBRACKET',
    (T.OP, ']'): 'RBRACKET'
}

_MAP1: dict[tuple[int, str], tuple[TT, str]] = {
    (T.NAME, 'label'): (TT.STATEMENT, 'label'),
    (T.OP, '@'): (TT.STATEMENT, 'label'),
    (T.NAME, 'goto'): (TT.STATEMENT, 'goto'),
    (T.OP, '->'): (TT.STATEMENT, 'goto'),
    (T.NAME, 'line'): (TT.STATEMENT, 'line'),
    (T.OP, '-'): (TT.STATEMENT, 'line'),
    (T.NAME, 'choice'): (TT.STATEMENT, 'choice'),
    (T.OP, '*'): (TT.STATEMENT, 'choice'),
    (T.NAME, 'map'): (TT.STATEMENT, 'map'),
    (T.OP, '**'): (TT.STATEMENT, 'map'),
    (T.NAME, 'as'): (TT.OPERATOR, 'as'),
    (T.OP, '=>'): (TT.OPERATOR, 'as'),
    (T.OP, '{'): (TT.OPERATOR, '{'),
    (T.OP, '}'): (TT.OPERATOR, '}'),
    (T.NAME, 'script'): (TT.STATEMENT, 'script'),
    (T.ERRORTOKEN, '$'): (TT.STATEMENT, 'script'),
    (T.OP, '|'): (TT.OPERATOR, '|'),
    (T.OP, ':'): (TT.OPERATOR, ':'),
    (T.NAME, 'if'): (TT.OPERATOR, 'if'),
}

_MAP2: dict[int, TT] = {
    T.NUMBER: TT.CONSTANT,
    T.STRING: TT.CONSTANT,
    T.NAME: TT.NAME,
    T.OP: TT.OPERATOR,
    T.INDENT: TT.INDENT,
    T.DEDENT: TT.DEDENT,
    T.NEWLINE: TT.NEWLINE,
    T.ENDMARKER: TT.END
}

# %%



def _tokens(instr: str):
    lines = (s+'\n' for s in instr.split('\n'))
    return T.generate_tokens(lambda: next(lines))


def _map_token(token: T.TokenInfo):
    typeint, value, pos, *_ = token
    typeval = _MAP1.get((typeint, value), None) or (
        _MAP2.get(typeint, TT.UNKNOWN), value)

    return Token(*typeval, pos)

def _postprocess(tokens: Iterable[T.TokenInfo]):
    outtokens: list[Token] = list()

    for token in tokens:
        tk = _map_token(token)

        if (tk.type, tk.value) == (TT.OPERATOR, '{'):
            pass
            

# %%


def _postproc_tokens(tokens: Iterable[Token]):
    out_tokens: list[Token] = list()
    code = list()
    store = False
    pos = tuple()
    for token in tokens:

        if token.type == TT.OPERATOR and token.value == '{':
            store = True
            pos = token.position
            continue

        if token.type == TT.OPERATOR and token.value == '}':
            out_tokens.append(Token(TokenType.EXPR, ' '.join(code), pos))
            store = False
            code.clear()
            continue

        if store:
            code.append(token.value)
        else:
            out_tokens.append(token)

    return (t for t in out_tokens if t.type != TokenType.EMPTY)


@singledispatch
def tokenize(code: Union[str, TextIOBase], raw=False) -> Generator[Union[Token, T.TokenInfo], None, None]:
    raise TypeError('code must be a str or TextIOBase.')


@tokenize.register
def tokenize_str(code: str, raw: bool = False):
    if raw:
        return _tokens(code)

    return _postproc_tokens(_map_token(t) for t in _tokens(code))


@tokenize.register
def tokenize_file(file: TextIOBase, raw: bool = False):
    code = file.read()
    return tokenize(code, raw)


# %%
tkns = []
with open('test2.zds', 'r') as f:
    tkns = list(tokenize_file(f, True))

# %%
