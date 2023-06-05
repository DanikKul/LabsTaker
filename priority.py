
def wrapper(func):
    def inner():
        print('lol')
        func()
        print('lol')
    return inner


@wrapper
def lol():
    print('asd')


if __name__ == "__main__":
    lol()
