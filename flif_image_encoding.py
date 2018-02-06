# -*- coding: utf-8 -*-
"""
Created on Sat Jan 20 21:18:10 2018

@author: Matthias Höffken
"""

from __future__ import print_function

__all__ = ["flifEncoderImage", "flifEncoder"]


import ctypes as ct
import numpy as np
from flif_wrapper_common import flifImageBase, flifEncoderBase

####################################################################################

# Logging

import logging
Logger = logging.getLogger("FLIF_Encoder")
Logger.setLevel("DEBUG")


####################################################################################



class flifEncoderImage( flifImageBase ):
    
    mImage = None
    mImporter = None
    
    mFlifImageHandle = None

    
    
    def __init__(self, npImage ):
        self.mImporter = self.getFlifImporter( npImage )
        self.mImage = self.correctImageStrides( npImage )


    def  __enter__(self):
        assert( 0 == (self.mImage.strides[0] % self.mImage.ndim) )
        self.mFlifImageHandle = self.mImporter( self.mImage.shape[1], self.mImage.shape[0], 
                                                self.mImage.ctypes.data_as( ct.c_void_p ), 
                                                self.mImage.strides[0] / self.mImage.ndim )
        
        Logger.debug("Using FLIF image importer %s", repr( self.mFlifImageHandle ) )
        
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.mFlifImageHandle is not None:
            self.flif.destroy_image( self.mFlifImageHandle )
            self.mFlifImageHandle = None
    
    
    @classmethod
    def getFlifImporter( cls, npImage ):
        
        flif = cls.flif
        
        # check images planes
        if 2 == npImage.ndim:
            # gray scale image
            imgType = "gray"
            importer = ( flif.import_image_GRAY, flif.import_image_GRAY16 )
        elif (3 == npImage.ndim) and (3 == npImage.shape[2]):
            # RGB Image
            imgType = "RGB"
            importer = ( flif.import_image_RGB, )
        elif (3 == npImage.ndim) and (4 == npImage.shape[2]):
            # RGBA Image
            imgType = "RGBA"
            importer = ( flif.import_image_RGBA, )
        else:
            raise ValueError( "Unsupported image shape '%s'" % repr(npImage.shape) )
        
        # check dtype
        if np.issubdtype( npImage.dtype, np.uint8 ):
            importer = importer[0]
        elif np.issubdtype( npImage.dtype, np.uint16 ) and (2==len(importer)):
            importer = importer[1]
        else:
            raise TypeError("image dtype '%s' in combination with '%s' not supported" % (repr(npImage.dtype), imgType))
        
        Logger.info( "Importing %s%d image", imgType, npImage.itemsize << 3 )
        
        return importer
    
    
    @staticmethod
    def correctImageStrides( npImage ):
        
        def isCopyRequired( npImage ):
            if npImage.strides[-1] != npImage.itemsize:
                return True
            
            if 3 == npImage.ndim:            
                if npImage.strides[1] != ( npImage.itemsize * npImage.shape[2] ):
                    return True
            
            return False
        
        if isCopyRequired( npImage ):
            Logger.info("Deep copy on image required")
            npImage = npImage.copy(order='C')
        
        assert( not isCopyRequired( npImage ) )
        
        return npImage
    

####################################################################################


class flifEncoder( flifEncoderBase ):

    
    # Object members
    mFlifEncoderHandle = None
    mFname = None
            
    mDoCrcCheck = None
    mInterlaced = None
    mLearnRepeat = None
    mSplitThreshold = None
    mMaxLoss = None
    
    
    def __init__(self, fname, crcCheck=True, interlaced=False, learn_repeat=4, split_threshold_factor=12, maxloss=0 ):
        self.mFname = fname
        
        self.mDoCrcCheck = int( bool(crcCheck) )
        self.mInterlaced = int( bool(interlaced) )
        self.mLearnRepeat = max( 0, int(learn_repeat) )
        self.mSplitThreshold = 5461 * 8 * max( 4, int(split_threshold_factor) )
        self.mMaxLoss = max( 0, min( 100, int(maxloss) ) )   
    
    
    def __del__(self):
        self.close()
    
    
    def  __enter__(self):
        self.open()
        return self
    
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()
        else:
            self.destroy()

    
    
    def open(self):
        # check if file is writable
        with open( self.mFname, "w" ) as ftest:
            pass        
        
        self.mFlifEncoderHandle = self.flif.create_encoder()
        Logger.debug("Create FLIF encoder %r", self.mFlifEncoderHandle )
        
        self.flif.set_interlaced( self.mFlifEncoderHandle, self.mInterlaced )
        self.flif.set_learn_repeat( self.mFlifEncoderHandle, self.mLearnRepeat )
        self.flif.set_split_threshold( self.mFlifEncoderHandle, self.mSplitThreshold )
        self.flif.set_crc_check( self.mFlifEncoderHandle, self.mDoCrcCheck )
        self.flif.set_lossy( self.mFlifEncoderHandle, self.mMaxLoss )
        
        return self
    
    
    def close(self):
        if self.mFlifEncoderHandle is not None:
            try:
                retval = self.flif.encode_file( self.mFlifEncoderHandle, self.mFname )
                if 1 != retval:
                    raise IOError("Error writing FLIF file %s" % self.mFname )
            finally:
                self.destroy()


    def destroy(self):
        if self.mFlifEncoderHandle is not None:
            handle = self.mFlifEncoderHandle
            self.mFlifEncoderHandle = None
            self.flif.destroy_encoder( handle )
            
    
    
    def addImage(self, img ):
        
        if self.mFlifEncoderHandle is not None:
            if isinstance( img, flifEncoderImage ):
                if img.mFlifImageHandle is not None:
                    self.flif.add_image( self.mFlifEncoderHandle, img.mFlifImageHandle )
            else:
                with flifEncoderImage( img ) as img:
                    self.moveImage( img )
    
    
    def moveImage(self, flifImage ):
        
        assert isinstance( flifImage, flifEncoderImage ), "%r is not a flifEncoderImage" % flifImage
        
        if (self.mFlifEncoderHandle is not None) and (flifImage.mFlifImageHandle is not None):
            self.flif.add_image_move( self.mFlifEncoderHandle, flifImage.mFlifImageHandle )
    

