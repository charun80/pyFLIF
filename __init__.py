# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 00:14:28 2018

@author: Matthias Höffken
"""

__all__ = [ "imread", "imwrite",\
            "flifEncoderImage", "flifEncoder",\
            "flifDecoderImage", "flifDecoder" ]


from flif_convenience import imwrite, imread
from flif_image_encoding import flifEncoderImage, flifEncoder
from flif_image_decoding import flifDecoderImage, flifDecoder
