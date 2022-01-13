def cash(old_func, __cash=None):
    if __cash is None:
        __cash = {}

    def new_func(*args):
        if args not in __cash:
            __cash[args] = old_func(*args)
        return __cash[args]
    return new_func
