from time import perf_counter as clock


class Timer:
    def __init__(self):
        self.avg = None

    def __enter__(self):
        self.start = clock()

    def __exit__(self, *a):
        self.total = clock() - self.start
        if self.avg:
            self.avg = (self.avg + self.total) / 2
        else:
            self.avg = self.total
