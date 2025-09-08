import itertools

def to_ranges(nums):
    for a, b in itertools.groupby(enumerate(nums), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]
