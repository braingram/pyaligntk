#!/usr/bin/env python

import cv2

import pylab

from .. import io


def show_match(image, reference, alignment_map):
    pylab.gray()
    # show reference
    pylab.subplot(221)
    pylab.imshow(reference)
    pylab.subplot(222)
    pylab.imshow(image)
    # TODO plot points
    image_pts, ref_pts = io.maps.resolve.to_corresponding_points(alignment_map)
    # warp image onto reference
    image_to_ref_affine = io.maps.resolve.to_affine(alignment_map)
    pass
