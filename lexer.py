# %%
import tokenize as T
from functools import singledispatch
from io import TextIOBase
from typing import Generator, Iterable
from tokens import Token, TokenType


_BUILTINS: dict[tuple[int, str], str] = {
    (T.NAME, 'label'): 'LABEL',
    (T.OP, '@'): 'LABEL',
    (T.NAME, 'goto'): 'GOTO',
    (T.OP, '->'): 'GOTO',
    (T.NAME, 'line'): 'LINE',
    (T.OP, '-'): 'LINE',
    (T.NAME, 'option'): 'OPTION',
    (T.OP, '*'): 'OPTION',
    (T.NAME, 'map'): 'MAP',
    (T.OP, '**'): 'MAP',
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

_TOKENMAP: dict[str, TokenType] = {
    'LABEL': TokenType.LABEL,
    'GOTO': TokenType.GOTO,
    'LINE': TokenType.LINE,
    'OPTION': TokenType.OPTION,
    'MAP': TokenType.MAP,
    'CODE': TokenType.CODE,
    'COLON': TokenType.COLON,
    'CONCAT': TokenType.CONCAT,
    'IF': TokenType.IF,
    'LBRACE': TokenType.LBRACE,
    'RBRACE': TokenType.RBRACE,
    'LBRACKET': TokenType.LBRACKET,
    'RBRACKET': TokenType.RBRACKET,
    'ENDMARKER': TokenType.END,
    'NEWLINE': TokenType.NEWLINE,
    'INDENT': TokenType.INDENT,
    'DEDENT': TokenType.DEDENT,
    'STRING': TokenType.STRING,
    'NAME': TokenType.NAME,
    'NL': TokenType.EMPTY,
    'COMMENT': TokenType.EMPTY
}


def _tokens(instr: str):
    lines = (s+'\n' for s in instr.split('\n'))
    return T.generate_tokens(lambda: next(lines))


def _map_token(token: T.TokenInfo):
    typeint, value, pos, *_ = token
    typename = _BUILTINS.get((typeint, value), None) or T.tok_name[typeint]

    return Token(_TOKENMAP.get(typename, TokenType.UNKNOWN), value, pos)


def _postproc_tokens(tokens: Iterable[Token]):
    out_tokens = list()
    code = list()
    store = False
    pos = tuple()
    for token in tokens:

        if token.type == TokenType.LBRACE:
            store = True
            pos = token.position
            continue

        if token.type == TokenType.RBRACE:
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
def tokenize(code, raw=False) -> Generator[Token, None, None]:
    raise TypeError('code must be a str or TextIOBase.')


@tokenize.register
def tokenize_str(code: str, raw=False) -> Generator[Token, None, None]:
    if raw:
        return _tokens(code)

    return _postproc_tokens(_map_token(t) for t in _tokens(code))


@tokenize.register
def tokenize_file(file: TextIOBase, raw=False) -> Generator[Token, None, None]:
    code = file.read()
    return tokenize(code, raw)

# %%
