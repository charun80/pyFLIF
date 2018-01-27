# -*- coding: utf-8 -*-
"""
Created on Sat Jan 27 20:48:58 2018

@author: Matthias Höffken
"""

__all__ = ["imwrite", "imread"]


import os.path
from flif_image_encoding import flifEncoder
from flif_image_decoding import flifDecoder


try:
    
    import scipy.misc
    genericImgReader = lambda pth: scipy.misc.imread(pth)
    genericImgWriter = lambda pth,img: scipy.misc.imsave(pth,img)
    
except ImportError:
    
    try:
        import cv2        
        genericImgReader = lambda pth: cv2.imread(pth)
        genericImgWriter = lambda pth,img: cv2.imwrite(pth,img)
    except ImportError:
        genericImgReader = None
        genericImgWriter = None


####################################################################################


def imwrite( pth, img ):
    ext = os.path.splitext( pth )[1]
    
    if ".flif" == ext.lower():
        with flifEncoder( pth ) as enc:
            return enc.addImage( img )
    elif genericImgReader is not None:
        return genericImgWriter( pth, img )
    else:
        raise IOError("%r is not a FLIF file" % pth) 


def imread( pth ):
    ext = os.path.splitext( pth )[1]
    
    if ".flif" == ext.lower():
        with flifDecoder( pth ) as dec:
            return dec.getImage(0)
    elif genericImgReader is not None:
        return genericImgReader( pth )
    else:
        raise IOError("%r is not a FLIF file" % pth)

