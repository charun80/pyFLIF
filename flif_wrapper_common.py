# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 18:53:09 2018

@author: Matthias Höffken
"""

from __future__ import print_function


__all__ = ["flifImageBase", "flifEncoderBase", "flifDecoderBase"]

import ctypes as ct
import os
import numpy as np


_FLIF_libName = "libflif.so"
_FLIF_libPath = os.path.join( os.path.dirname( os.path.abspath(__file__) ) , "FLIF", "src" )


# Logging
import logging
Logger = logging.getLogger("FLIF_wrapper_common")
Logger.setLevel("DEBUG")




class flifImageBase( object ):
        
    class flif(object):
        get_width = None
        get_height = None
        get_nb_channels = None
        get_depth = None
        get_palette_size = None
        
        import_image_RGBA = None
        import_image_RGB = None
        import_image_GRAY = None
        import_image_GRAY16 = None
        
        read_row_GRAY8  = None
        read_row_GRAY16 = None
        read_row_RGBA8  = None
        read_row_RGBA16 = None        
        
        destroy_image = None
        
    
    @classmethod
    def initialize(cls, fliflib ):
        Logger.debug("Initializing flifImageBase")
        
        strct = cls.flif
        
        imgGetter    =  [ "width",     "height",    "nb_channels", "depth",    "palette_size" ]
        getterResType = [ ct.c_uint32, ct.c_uint32, ct.c_uint8,    ct.c_uint8, ct.c_uint32 ]
        
        for getter, rtype in zip( imgGetter, getterResType ):
            strct_getter = "get_%s" % getter
            setattr( strct, strct_getter,
                     fliflib.__getitem__("flif_image_get_%s" % getter) )
            strct.__dict__[strct_getter].argtypes = [ ct.c_void_p ]
            strct.__dict__[strct_getter].restype  = rtype
        
        
        imgImporters = [ "RGBA", "RGB", "GRAY", "GRAY16" ]        
        #                        width        height       data   major-stride
        importArgTypes = [ ct.c_uint32, ct.c_uint32, ct.c_void_p, ct.c_uint32 ]
        
        for importer in imgImporters:
            strct_importer = "import_image_%s" % importer
            setattr( strct, strct_importer,
                     fliflib.__getitem__("flif_import_image_%s" % importer) )
            strct.__dict__[strct_importer].argtypes = importArgTypes
            strct.__dict__[strct_importer].restype = ct.c_void_p        
        
        
        rowReader = [ "GRAY8", "GRAY16", "RGBA8", "RGBA16" ]
        readerArgs = [ ct.c_void_p, ct.c_uint32, ct.c_void_p, ct.c_size_t ]
        
        for Reader in rowReader:
            strct_reader = "read_row_%s" % Reader
            setattr( strct, strct_reader, 
                     fliflib.__getitem__("flif_image_read_row_%s" % Reader) )
            strct.__dict__[strct_reader].restype = None
            strct.__dict__[strct_reader].argtypes = readerArgs
        
        
        strct.destroy_image = fliflib.flif_destroy_image
        strct.destroy_image.argtypes = [ ct.c_void_p ]




class flifEncoderBase( object ):
    
    class flif(object):
        create_encoder = None
        encode_file = None
        destroy_encoder = None
        
        add_image = None
        add_image_move = None
        
        set_crc_check = None
    
    
    @classmethod
    def initialize(cls, fliflib ):
        Logger.debug("Initializing flifEncoder")
        
        strct = cls.flif
        
        strct.create_encoder = fliflib.flif_create_encoder
        strct.create_encoder.restype = ct.c_void_p
        
        strct.encode_file = fliflib.flif_encoder_encode_file
        strct.encode_file.restype = ct.c_int32
        strct.encode_file.argtypes = [ ct.c_void_p, ct.c_char_p ]
        
        strct.destroy_encoder = fliflib.flif_destroy_encoder
        strct.destroy_encoder.restype = None
        strct.destroy_encoder.argtypes = [ ct.c_void_p ]
        
        strct.add_image = fliflib.flif_encoder_add_image
        strct.add_image.restype = None
        strct.add_image.argtypes = [ ct.c_void_p, ct.c_void_p ]
        
        strct.add_image_move = fliflib.flif_encoder_add_image_move
        strct.add_image_move.restype = None
        strct.add_image_move.argtypes = [ ct.c_void_p, ct.c_void_p ]

        strct.set_crc_check = fliflib.flif_encoder_set_crc_check
        strct.set_crc_check.restype = None
        strct.set_crc_check.argtypes = [ ct.c_void_p, ct.c_uint32 ]




class flifDecoderBase( object ):
    
    class flif(object):
        create_decoder = None
        decode_file = None
        set_crc_check = None
        
        num_images = None
        get_image = None
        
        destroy_decoder = None
    
    
    @classmethod
    def initialize(cls, fliflib ):
        Logger.debug("Initializing flifDecoder")
        
        strct = cls.flif
        
        strct.create_decoder = fliflib.flif_create_decoder
        strct.create_decoder.restype = ct.c_void_p
        
        strct.decode_file = fliflib.flif_decoder_decode_file
        strct.decode_file.restype = ct.c_int32
        strct.decode_file.argtypes = [ ct.c_void_p, ct.c_char_p ]
        
        strct.set_crc_check = fliflib.flif_decoder_set_crc_check
        strct.set_crc_check.restype = None
        strct.set_crc_check.argtypes = [ ct.c_void_p, ct.c_uint32 ]
        
        strct.num_images = fliflib.flif_decoder_num_images
        strct.num_images.restype = ct.c_size_t
        strct.num_images.argtypes = [ ct.c_void_p ]
        
        strct.get_image = fliflib.flif_decoder_get_image
        strct.get_image.restype = ct.c_void_p
        strct.get_image.argtypes = [ ct.c_void_p, ct.c_size_t ]
        
        strct.destroy_decoder = fliflib.flif_destroy_decoder
        strct.destroy_decoder.restype = None
        strct.destroy_decoder.argtypes = [ ct.c_void_p ]


####################################################################################
## Loading DLL or shared library file


def _loadFLIF_Library():
    Logger.debug( "Loading FLIF library under %s", os.path.join( _FLIF_libName, _FLIF_libPath ) )
    fliflib = np.ctypeslib.load_library( _FLIF_libName, _FLIF_libPath )
    
    flifEncoderBase.initialize( fliflib )
    flifImageBase.initialize( fliflib )
    flifDecoderBase.initialize( fliflib )

_loadFLIF_Library()




