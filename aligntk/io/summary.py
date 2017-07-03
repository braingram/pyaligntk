#!/usr/bin/env python

import os


columns = [
    'image', 'reference', 'correlation', 'distortion', 'correspond',
    'constrain', 'energy']
dtypes = [
    str, str, float, float, float, float, float]


def read(filename, map_name=True):
    """
    Header:
    Sorted by slice:
    IMAGE    REFERENCE  ...

    image, reference, correlation, distortion, correspond, constrain, energy
    """
    d = []
    filename = os.path.abspath(os.path.expanduser(filename))
    with open(filename, 'r') as f:
        for l in f:
            if l[:5] == 'IMAGE':
                break
        for l in f:
            l = l.strip()
            if len(l) == 0:
                break
            ts = l.split()
            assert len(ts) == len(columns)
            d.append({
                c: dt(t) for (c, t, dt) in zip(columns, ts, dtypes)})
    if map_name:
        return add_map_name(d)
    return d


def add_map_name(d):
    for i in xrange(len(d)):
        img = d[i]['image']
        ref = d[i]['reference'].split('/')[-1]
        d[i]['map'] = '%s_%s' % (img, ref)
    return d


def write_map_list(d, filename):
    if len(d) and 'map' not in d[0]:
        d = add_map_name(d)
    filename = os.path.abspath(os.path.expanduser(filename))
    with open(filename, 'w') as f:
        for i in d:
            f.write('%s %s %s\n' % (i['image'], i['reference'], i['map']))
