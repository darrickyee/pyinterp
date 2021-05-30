# %%
import dis


def m():

    def myfunc(i):
        print(f'Ok {i}')

    def run(a):

        x = 5

        if x % 2:
            myfunc(a)
            print('x is even')

        print('End')

    for i in range(3):
        run(i)


# %%
dis.dis(m)

# %%
