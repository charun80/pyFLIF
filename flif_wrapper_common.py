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
Logger.setLevel("WARN")




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
        
        strct.destroy_image = fliflib.flif_destroy_image
        strct.destroy_image.argtypes = [ ct.c_void_p ]
        
        def configCallGeneral( flif_prefix, name, argtypes=None, restype=None ):
            setattr( strct, name,
                     fliflib.__getitem__("%s_%s" % (flif_prefix, name) ) )
            if argtypes is not None:
                strct.__dict__[name].argtypes = argtypes 
            strct.__dict__[name].restype  = restype
        
        # Image import function
        imgImporters = [ "RGBA", "RGB", "GRAY", "GRAY16" ]        
        #                        width        height       data   major-stride
        importArgTypes = [ ct.c_uint32, ct.c_uint32, ct.c_void_p, ct.c_uint32 ]
        configImportCall = lambda name: configCallGeneral( "flif", name, importArgTypes, ct.c_void_p )
        
        for importer in imgImporters:
            configImportCall( "import_image_%s" % importer )


        # Getter functions    
        imgGetter    =  [ "width",     "height",    "nb_channels", "depth",    "palette_size" ]
        getterResType = [ ct.c_uint32, ct.c_uint32, ct.c_uint8,    ct.c_uint8, ct.c_uint32 ]
        configGetterCall = lambda name, rtype: configCallGeneral( "flif_image", name, [ ct.c_void_p ], rtype )
        
        for getter, rtype in zip( imgGetter, getterResType ):
            configGetterCall( "get_%s" % getter, rtype )
        
        
        # Row Reader
        rowReader = [ "GRAY8", "GRAY16", "RGBA8", "RGBA16" ]
        readerArgs = [ ct.c_void_p, ct.c_uint32, ct.c_void_p, ct.c_size_t ]
        configReaderCall = lambda name: configCallGeneral( "flif_image", name, readerArgs )
        
        for Reader in rowReader:
            configReaderCall( "read_row_%s" % Reader )



class flifEncoderBase( object ):
    
    class flif(object):
        create_encoder = None
        destroy_encoder = None
        
        set_interlaced = None
        set_learn_repeat = None
        set_split_threshold = None
        set_crc_check = None
        set_lossy = None
                
        encode_file = None

        add_image = None
        add_image_move = None
        
        
    
    
    @classmethod
    def initialize(cls, fliflib ):
        Logger.debug("Initializing flifEncoder")
        
        strct = cls.flif
        
        strct.create_encoder = fliflib.flif_create_encoder
        strct.create_encoder.restype = ct.c_void_p
        
        strct.destroy_encoder = fliflib.flif_destroy_encoder
        strct.destroy_encoder.restype = None
        strct.destroy_encoder.argtypes = [ ct.c_void_p ]
        
        
        def configCall( name, argtypes=None, restype=None ):
            setattr( strct, name,
                     fliflib.__getitem__("flif_encoder_%s" % name) )
            if argtypes is not None:
                strct.__dict__[name].argtypes = argtypes 
            strct.__dict__[name].restype  = restype
        
        
        configCall( "encode_file", [ ct.c_void_p, ct.c_char_p ], ct.c_int32 )
        configCall( "add_image", [ ct.c_void_p, ct.c_void_p ] )
        configCall( "add_image_move", [ ct.c_void_p, ct.c_void_p ] )
        
        configCall( "set_interlaced", [ ct.c_void_p, ct.c_uint32 ] )
        configCall( "set_learn_repeat", [ ct.c_void_p, ct.c_uint32 ] )
        configCall( "set_split_threshold", [ ct.c_void_p, ct.c_int32 ] )
        configCall( "set_crc_check", [ ct.c_void_p, ct.c_uint32 ] )
        configCall( "set_lossy", [ ct.c_void_p, ct.c_int32 ] )



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
                        
        strct.destroy_decoder = fliflib.flif_destroy_decoder
        strct.destroy_decoder.restype = None
        strct.destroy_decoder.argtypes = [ ct.c_void_p ]
        
        
        def configCall( name, argtypes=None, restype=None ):
            setattr( strct, name,
                     fliflib.__getitem__("flif_decoder_%s" % name) )
            if argtypes is not None:
                strct.__dict__[name].argtypes = argtypes 
            strct.__dict__[name].restype  = restype
        
        configCall( "decode_file", [ ct.c_void_p, ct.c_char_p ], ct.c_int32 )
        configCall( "set_crc_check", [ ct.c_void_p, ct.c_uint32 ] )
        configCall( "num_images", [ ct.c_void_p ], ct.c_size_t )
        configCall( "get_image", [ ct.c_void_p, ct.c_size_t ], ct.c_void_p )



####################################################################################
## Loading DLL or shared library file


def _loadFLIF_Library():
    Logger.debug( "Loading FLIF library under %s", os.path.join( _FLIF_libName, _FLIF_libPath ) )
    fliflib = np.ctypeslib.load_library( _FLIF_libName, _FLIF_libPath )
    
    flifEncoderBase.initialize( fliflib )
    flifImageBase.initialize( fliflib )
    flifDecoderBase.initialize( fliflib )

_loadFLIF_Library()




