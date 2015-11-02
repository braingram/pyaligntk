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


def to_affine(alignment_map, confidence_threshold=0.8, full=True):
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
