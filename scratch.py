# %%
from lang import utils

# %%
PRS = None
with open('lang/dlg.gram', 'r') as f:
    PRS = utils.generate_parser(utils.generate_grammar(f), 'lang/dlgparser.py')
# %%
import ast
from lang.dlgparser import GeneratedParser as MyParser

with open('dlgtest.txt', 'r') as dlg:
    res = utils.run_parser(dlg, MyParser, verbose=True)
    print(ast.dump(res, indent=2))
# %%
