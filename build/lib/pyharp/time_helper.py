from time import gmtime, localtime, strftime
def get_time(local = True):
    current_time = localtime() if local else gmtime()
    return strftime("%a, %d %b %I:%M:%S%p", current_time)
