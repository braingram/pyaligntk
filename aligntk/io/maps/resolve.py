#!/usr/bin/env python

import cv2
import numpy
import scipy.interpolate


def to_level(alignment_map, level):
    if alignment_map['level'] == level:
        return alignment_map
    from_scale = float(1 << alignment_map['level'])
    to_scale = 1. / (1 << level)
    new_elements = []
    x_min = float(alignment_map['x_min'])
    y_min = float(alignment_map['y_min'])
    for e in alignment_map['elements']:
        x, y, c = e
        nx = (x + x_min) * from_scale
        ny = (y + y_min) * from_scale
        new_elements.append((nx, ny, c))
    return new_elements


def to_corresponding_points(alignment_map, confidence_threshold=0.8):
    from_scale = float(1 << alignment_map['level'])
    ref_pts = []
    image_pts = []
    x_min = float(alignment_map['x_min'])
    y_min = float(alignment_map['y_min'])
    width = float(alignment_map['width'])
    height = float(alignment_map['height'])
    for (ei, e) in enumerate(alignment_map['elements']):
        x, y, c = e
        if c < confidence_threshold:
            continue
        rx = (x + x_min) * from_scale
        ry = (y + y_min) * from_scale
        iy, ix = divmod(ei, width)
        ix = ix / (width - 1.) * from_scale
        iy = iy / (height - 1.) * from_scale
        ref_pts.append((rx, ry))
        image_pts.append((ix, iy))
    return image_pts, ref_pts


def from_affine(affine, im, **info):
    # level, elements, width, height, x_min, y_min, image, ref
    assert 'image' in info
    assert 'ref' in info
    if 'level' not in info:
        info['level'] = int(numpy.floor(numpy.log2(min(im.shape))))
    lvl = info['level']
    info['width'] = (im.shape[1] >> info['level']) + 1
    info['height'] = (im.shape[1] >> info['level']) + 1
    info['x_min'] = 0
    info['y_min'] = 0
    elements = []
    sa = numpy.matrix(numpy.vstack((
        affine, numpy.array([(0., 0., 1.), ])))).T
    to_lvl_scale = 1. / (1 << lvl)
    for y in xrange(info['height']):
        for x in xrange(info['width']):
            px = (x << lvl)
            py = (y << lvl)
            # convert x, y to ref coordinates
            pt = numpy.array(numpy.array([px, py, 1.0]) * sa)[0]
            elements.append((
                pt[0] * to_lvl_scale, pt[1] * to_lvl_scale, 1.0))
            print x, y, px, py, elements[-1]
    info['elements'] = elements
    return info


def to_affine(alignment_map, confidence_threshold=0.8, full=False):
    """ Returns a image-to-ref affine """
    image_pts, ref_pts = to_corresponding_points(
        alignment_map, confidence_threshold=confidence_threshold)
    return cv2.estimateRigidTransform(
        numpy.array(image_pts), numpy.array(ref_pts), full)


def to_dense_remap(alignment_map, confidence_threshold=0.8):
    image_pts, ref_pts = to_corresponding_points(
        alignment_map, confidence_threshold=confidence_threshold)
    # grid data
    w = (alignment_map['width'] - 1) << alignment_map['level']
    wc = w * 1j
    h = (alignment_map['height'] - 1) << alignment_map['level']
    hc = h * 1j
    g_x, g_y = numpy.mgrid[0:w-1:wc, 0:h-1:hc]
    #g_z = scipy.interpolate.griddata(
    #    ref_pts, image_pts, (g_x, g_y), method='cubic')
    g_z = scipy.interpolate.griddata(
        image_pts, ref_pts, (g_y, g_x), method='cubic')
    m_x = numpy.append([], [ar[:, 1] for ar in g_z]).reshape(w, h).astype('f4')
    m_y = numpy.append([], [ar[:, 0] for ar in g_z]).reshape(w, h).astype('f4')
    return m_x, m_y
