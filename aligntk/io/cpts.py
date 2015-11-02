#!/usr/bin/env python

import cv2
import numpy


def read_cpts(fn):
    """ Returns: image_points, reference_points
    where points are (x, y) pairs relative to either the image or reference"""
    pts = numpy.loadtxt(fn, dtype='f8')
    if len(pts) == 0:
        return [], []
    return pts[:, :2], pts[:, 2:]


def write_cpts(pts, fn):
    pass


def to_affine(image_points, reference_points, full=False):
    return cv2.estimateRigidTransform(
        numpy.array(image_points), numpy.array(reference_points), full)


def to_dense_map(image_points, reference_points):
    pass
