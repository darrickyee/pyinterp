# %%
from io import StringIO
from token import tok_name
from tokenize import TokenInfo, generate_tokens

# %%


def gt(code_str: str):
    return list(generate_tokens(StringIO(code_str).readline))

# %%



TOK_MAP = {
    (1, 'line'): TokenInfo()
}

# %%


sample = '''
section Start
line player: "Hello there!"
- 'Bob': "Hi, {player}."
'''
# %%
