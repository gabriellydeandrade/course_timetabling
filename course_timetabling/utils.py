from itertools import groupby, islice, product

def take(n, iterable):
    "Return first n items of the iterable as a list."
    return list(islice(iterable, n))

def all_equal(iterable, key=None):
    "Returns True if all the elements are equal to each other."
    return len(take(2, groupby(iterable, key))) <= 1

# print(all_equal([1,2]))

def cartesian(iterable):
    elements = []
    for elem in product(*iterable):
        if len(elem[0].split(",")) < len(elem[1].split(",")):
            continue
        elements.append(elem)
    return elements

