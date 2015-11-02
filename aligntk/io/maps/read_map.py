#!/usr/bin/env python

import struct


fn = 'q0q1.map'

# map element = x y c (floats)


def read_map(fn):
    """
    level = 1 << level downscale of grid
    x_min = post level (downscale) x_min position in image
    y_min ...
    width = post level (downscale)
    height = ...
    image = image that will be mapped to reference
    ref = image that used as ref
    elements = (x, y, c)
        x = x position in ref (post level)
        y = y position in ref (post level)
        c = confidence (0->1)
    elements is actually a 2d array with x changing fastest =
        [y0x0, y0x1, y0x2.... y(h-1)x(w-1)]
    """
    info = {}
    with open(fn, 'rb') as f:
        l = f.readline()
        assert l.strip() == 'M1'
        l = f.readline()
        level = int(l.strip())
        l = f.readline()
        width, height = map(int, l.strip().split())
        l = f.readline()
        x_min, y_min = map(int, l.strip().split())
        l = f.readline()
        im_name, ref_name = l.strip().split()
        elements = []
        for _ in xrange(width * height):
            elements.append(struct.unpack('fff', f.read(12)))
        info['level'] = level
        info['width'] = width
        info['height'] = height
        info['x_min'] = x_min
        info['y_min'] = y_min
        info['elements'] = elements
        info['image'] = im_name
        info['ref'] = ref_name
    return info


def write_map(m, fn):
    assert 'level' in m
    assert 'elements' in m
    assert 'width' in m
    assert 'height' in m
    assert 'x_min' in m
    assert 'y_min' in m
    assert 'image' in m
    assert 'ref' in m
    assert len(m['elements']) == m['width'] * m['height']
    assert all([len(e) == 3 for e in m['elements']])
    with open(fn, 'wb') as f:
        f.write('M1\n')
        f.write('%i\n' % m['level'])
        f.write('%i %i\n' % (m['width'], m['height']))
        f.write('%i %i\n' % (m['x_min'], m['y_min']))
        f.write('%s %s\n' % (m['image'], m['ref']))
        for e in m['elements']:
            f.write(struct.pack('fff', *e))


def fake_model(name):
    m = {}
    m['level'] = 6
    m['width'] = 32
    m['height'] = 32
    m['image'] = name
    m['ref'] = 'grid'
    m['x_min'] = 0
    m['y_min'] = 0
    m['elements'] = []
    for y in xrange(32):
        for x in xrange(32):
            m['elements'].append((float(x), float(y), 1.0))
    return m


def gen_fake_models():
    for i in xrange(4):
        q = 'q%i' % i
        write_map(fake_model(q), 'models/%s.map' % q)


def fake_to_left(image, ref):
    m = {
        'x_min': 28,
        'y_min': 0,
        'level': 6,
        'width': 4,
        'height': 32,
        'image': image,
        'ref': ref,
    }
    m['elements'] = []
    for y in xrange(m['height']):
        for x in xrange(m['width']):
            m['elements'].append((float(x), float(y), 1.0))
    return m


def fake_to_top(image, ref):
    m = {
        'x_min': 0,
        'y_min': 28,
        'level': 6,
        'width': 32,
        'height': 4,
        'image': image,
        'ref': ref,
    }
    m['elements'] = []
    for y in xrange(m['height']):
        for x in xrange(m['width']):
            m['elements'].append((float(x), float(y), 1.0))
    return m


def gen_fake_maps():
    write_map(fake_to_left('q0', 'q1'), 'maps/q0q1.map')
    write_map(fake_to_top('q0', 'q2'), 'maps/q0q2.map')
    write_map(fake_to_top('q1', 'q3'), 'maps/q1q3.map')
    write_map(fake_to_left('q2', 'q3'), 'maps/q2q3.map')


def gen_fake():
    gen_fake_maps()
    gen_fake_models()
