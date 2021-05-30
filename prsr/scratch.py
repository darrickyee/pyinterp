# %%
import ast
import importlib.util
import io
import os
import pathlib
import sys
import textwrap
import token
import tokenize
from typing import IO, Any, Dict, Final, Type, cast

from pprint import pprint
from pegen.grammar import Grammar
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.parser import Parser
from pegen.python_generator import PythonParserGenerator
from pegen.tokenizer import Tokenizer
# %%
intmap = {
    '{': 25,
    '}': 26
}


def remap(tk: tokenize.TokenInfo):
    # if tk.string in ('{', '}'):
    #     token_dict = {**tk._asdict(), 'type': intmap[tk.string]}

    #     return tokenize.TokenInfo(*tuple(token_dict.values()))

    return tk


def parse_string(source: str):
    f = io.StringIO(source)

    tknizer = Tokenizer(remap(t) for t in tokenize.generate_tokens(f.readline))
    prs = GrammarParser(tknizer)
    return prs.start()


def generate_parser(grammar: Grammar, custom_nodes=None):
    custom_nodes = custom_nodes or {}
    out = io.StringIO()
    gnr = PythonParserGenerator(
        grammar, out, tokens={**token.tok_name})
    gnr.generate('<string>')
    ns: Dict[str, Any] = custom_nodes
    print(out.getvalue())
    exec(out.getvalue(), ns)
    return ns["GeneratedParser"]


def run_parser(infile: IO[str], parser_class: Type[Parser], *, verbose: bool = False) -> Any:
    # Run a parser on a file (stream).
    # type: ignore # typeshed issue #3515
    tokenizer = Tokenizer(remap(t)
                          for t in tokenize.generate_tokens(infile.readline))
    parser = parser_class(tokenizer, verbose=verbose)
    result = parser.start()
    if result is None:
        raise parser.make_syntax_error()
    return result


def gt(s: str):
    return list(remap(t) for t in tokenize.generate_tokens(io.StringIO(s).readline) if t.type != 61)


# %%
TK = []
GRM = []


def genprs(path: str):
    with open(path, 'r') as infile:
        tknizer = Tokenizer(remap(t)
                            for t in tokenize.generate_tokens(infile.readline))
        TK.append(tknizer)
        prs = GrammarParser(tknizer, verbose=True)
        GRM.append(prs.start())
        return generate_parser(GRM[-1])


gn = genprs('prsr/mygram.gram')
# gn = genprs('prsr/testgram.gram')

# %%

test_script = """
# Script statement
=== Simple

{x} choice '4'

=== Block
    {j==4} - 'hello'

        * 'Say \\'hello\\' back.'
    * 'Leave.'
        - "I'M LEAVING"
        - 'Go somewhere'

    {x==4}
        choice 'ffs'
        - 'Ok then'

    -> jj
    -> {'Simple' if x else 'Block'}

"""
# %%

with open('prsr/dlgtest.txt', 'r') as scr:
    res = run_parser(scr, gn, verbose=True)
    print('\n')
    pprint(res)
# %%
mycode = '''
def addx(x):
    def _add(y):
        return x + y

    return _add

add5 = addx(5)
add2 = addx(2)
add2(2) * add5(2)
'''
pprint(ast.dump(ast.parse(mycode)))
# %%
