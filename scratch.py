# %%
import dis


def main():

    def addx(x):
        def add(y):
            return x + y
        return add

    add5 = addx(5)
    add2 = addx(2)

    mult = True
    if mult:
        print(f'{add5(3) * add2(2)}')

    print('done')

dis.dis(main)
# %%
