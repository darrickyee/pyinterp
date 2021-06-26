import io
import tokenize
from typing import IO, Type

from pegen.grammar import Grammar
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.parser import Parser
from pegen.python_generator import PythonParserGenerator
from pegen.tokenizer import Tokenizer


def generate_grammar(infile: IO[str], verbose: bool = False):
    """Generates Grammar object using supplied text input stream.

    Args:
        infile (IO[str]): [description]
    """

    tknizer = Tokenizer(tokenize.generate_tokens(infile.readline))
    return GrammarParser(tknizer, verbose=verbose).start()


def generate_parser(grammar: Grammar, outfile: str = None):
    """Generates Python-based parser using supplied Grammar object.

    Args:
        grammar (Grammar): [description]

    Returns:
        Parser: Parser class
    """

    out = io.StringIO()
    gnr = PythonParserGenerator(grammar, out)
    gnr.generate('<string>')
    outstr = out.getvalue()
    if outfile:
        with open(outfile, 'w') as otf:
            otf.write(outstr)

    ns = {}
    exec(out.getvalue(), globals(), ns)
    return ns["GeneratedParser"]


def run_parser(infile: IO[str], parser_class: Type[Parser], *, verbose: bool = False):
    tknizer = Tokenizer(tokenize.generate_tokens(infile.readline))
    parser = parser_class(tknizer, verbose=verbose)
    result = parser.start()
    if result is None:
        raise parser.make_syntax_error()
    return result
