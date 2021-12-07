def index_contains(l, substring):
    for i, s in enumerate(l):
        if substring in str(s):
            return i
    return -1
    