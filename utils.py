import random
# import math

def get_table_sampler(table):
    if table is None:
        return None
    vals = []
    dist = []
    for k, v in table.items():
        vals.append(k)
        dist.append(v)
    def sampler():
        return random.choices(vals, dist, k=1)[0]

    return sampler

def get_major_scale(root, low, high):
    notes = []
    degrees = set([0, 2, 4, 5, 7, 9, 11])
    for note in range(low, high + 1):
        diff = note - root
        if diff % 12 in degrees:
            notes.append(note)

    return notes
