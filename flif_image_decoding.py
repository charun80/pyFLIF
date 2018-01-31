# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 18:09:13 2018

@author: Matthias Höffken
"""

from __future__ import print_function


__all__ = ["flifDecoderImage", "flifDecoder"]


import ctypes as ct
import numpy as np
from flif_wrapper_common import flifImageBase, flifDecoderBase

####################################################################################

# Logging

import logging
Logger = logging.getLogger("FLIF_Decoder")
Logger.setLevel("WARN")


####################################################################################


class flifDecoderImage( flifImageBase ):
    
    mFlifImageHandle = None
    
    @property
    def width(self):        return self.flif.get_width( self.mFlifImageHandle )
    @property
    def height(self):       return self.flif.get_height( self.mFlifImageHandle )
    @property
    def nb_channels(self):  return self.flif.get_nb_channels( self.mFlifImageHandle )
    @property
    def depth(self):        return self.flif.get_depth( self.mFlifImageHandle )
    @property
    def palette_size(self): return self.flif.get_palette_size( self.mFlifImageHandle )
    
    
    rowReader = None
    dtype     = None
    mImgShape = None
    
    
    def __init__(self, flifImageHandle ):
        self.mFlifImageHandle = flifImageHandle
        
        if 0 != self.palette_size:
            raise ValueError("")
        
        dtype = (np.uint8, np.uint16)
        
        if 1 == self.nb_channels:
            rowReader = ( self.flif.read_row_GRAY8, self.flif.read_row_GRAY16 )
            self.mImgShape = (self.height, self.width)
        else:
            rowReader = ( self.flif.read_row_RGBA8, self.flif.read_row_RGBA16 )
            self.mImgShape = (self.height, self.width, 4)
        
        if 8 == self.depth:
            self.dtype = dtype[0]
            rowReader = rowReader[0]
        elif 16 == self.depth:
            self.dtype = dtype[1]
            rowReader = rowReader[1]
        else:
            assert( False )  # depth should be always 8 or 16
        
        self.rowReader = lambda rowIdx, Buffer, bufSize: \
                                rowReader( self.mFlifImageHandle, rowIdx, Buffer, bufSize )
        

    
    def getImage( self ):
        
        auxShape = (self.mImgShape[0], np.prod(self.mImgShape[1:] ))
        
        npyImg = np.zeros( auxShape, dtype=self.dtype )
        assert( npyImg.flags['C_CONTIGUOUS'] )

        imgPointer = npyImg.ctypes.data_as( ct.c_void_p )
        
        for rowIdx in xrange( npyImg.shape[0] ):
            self.rowReader( rowIdx, imgPointer, npyImg.strides[0] )
            imgPointer.value += npyImg.strides[0]   # jump to next row (strides in bytes)
        
        npyImg = npyImg.reshape( self.mImgShape )
        
        if (1 < self.nb_channels) and (4 != self.nb_channels):
            npyImg = npyImg[:,:,:self.nb_channels]
        
        return npyImg


            

class flifDecoder( flifDecoderBase ):

    
    # Object members
    mFlifDecoderHandle = None
    mFname = None
    
    
    def __init__(self, fname ):
        self.mFname = fname
        self.mFlifDecoderHandle = None
    
    
    def  __enter__(self):
        # create decoder
        self.mFlifDecoderHandle = self.flif.create_decoder()
        Logger.debug("Create FLIF decoder %r", self.mFlifDecoderHandle )
        
        # set CRC check
        self.flif.set_crc_check( self.mFlifDecoderHandle, 1 )
        
        # encode file
        if 0 == self.flif.decode_file( self.mFlifDecoderHandle, self.mFname ):
            raise IOError("Error decoding FLIF file %r" % self.mFname )
        
        Logger.debug("Decoded FLIF file %r", self.mFname )
        
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.mFlifDecoderHandle is not None:
            self.flif.destroy_decoder( self.mFlifDecoderHandle )
            self.mFlifDecoderHandle = None
    
    
    def numImages(self):
        if self.mFlifDecoderHandle is None:
            raise IOError( "FLIF file %r not (yet) decoded" % self.mFname )
        return self.flif.num_images( self.mFlifDecoderHandle )
    
    
    def getImage(self, index ):
        if index >= self.numImages():
            raise ValueError("Frame index %d out of %d requested" % (index, self.numImages) )
        
        # optain image pointer
        flifImageHandle = self.flif.get_image( self.mFlifDecoderHandle, index )
        
        if flifImageHandle is None:
            raise IOError("Error reading image %d" % index)
        
        return flifDecoderImage( flifImageHandle ).getImage()
        
