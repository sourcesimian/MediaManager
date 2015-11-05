
# print "map = ("
# max = 1024
# divisor = 1
# for (s, f) in (('B', '%.0f'), ('kiB', '%.0f'), ('MiB', '%.1f'), ('GiB', '%.1f'), ('TiB', '%.2f')):
#     print "    (%d, %d, '%s', '%s')," % (max, divisor, s, f)
#     divisor = max
#     max *= 1024
# print ")"


def humanize(i):
    if not isinstance(i, int):
        return i

    map = (
        (1024, 1, 'B', '%.0f'),
        (1048576, 1024, 'kiB', '%.0f'),
        (1073741824, 1048576, 'MiB', '%.0f'),
        (1099511627776, 1073741824, 'GiB', '%.1f'),
        (1125899906842624, 1099511627776, 'TiB', '%.2f'),
    )

    for max, dividor, suffix, format in map:
        if i < max:
            return (format + '%s') % ((i/dividor), suffix)
    return i
