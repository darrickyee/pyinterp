# %%
GO = True


def nodegen(*args):
    i = 0
    while i < len(args):
        if GO:
            yield args[i]
            i += 1
        else:
            yield 'Waiting'

    return None


g = nodegen('hi', 'how are you', 'fuck off')

# %%
