from math import ceil


def spread_id(seq, num):
    """
    generator returning equally distributet indices of
    provided sequence.
    eg:
    a = np.linspace(0,1,100)
    print spread_id(a,10) <- will print 10, 20, 30, ...
    """
    length = float(len(seq))
    for i in range(num):
        yield int(ceil(i * length / num))


def spread(seq, num):
    """
    generator returning equally distributet elements
    in provided sequence.
    eg:
    a = np.linspace(0,1,100)
    print spread(a,10) <- will print 0.1, 0.2, 0.3, ...
    """
    for i in spread_id(seq, num):
        yield seq[i]


