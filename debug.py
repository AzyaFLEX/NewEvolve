def time_test(old_func):
    def new_func(*args, **kwargs):
        import datetime
        time1 = datetime.datetime.now()
        result = old_func(*args, **kwargs)
        time2 = datetime.datetime.now()
        print(time2 - time1)
        return result
    return new_func
