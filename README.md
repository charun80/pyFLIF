[_metadata_:redirect]:- "https://codeberg.org/monilophyta/imageio-flif"

# Deprecated

Please use the [imageio](https://imageio.github.io/) plugin [imageio-flif](https://codeberg.org/monilophyta/imageio-flif).

## pyFLIF: ctypes based Python wrapper for Free Lossless Image Format

### Build Instructions

#### Install the dependencies

##### FLIF dependencies

pyFLIF imports the [FLIF](https://github.com/FLIF-hub/FLIF) library as a sub-module. Please have a look [here](https://github.com/FLIF-hub/FLIF#install-the-dependencies) for [FLIF](https://github.com/FLIF-hub/FLIF) library dependencies.

##### pyFLIF dependencies

 - numpy: `sudo apt-get install python-numpy` (on debian/ubuntu)
 - scipy (optional): `sudo apt-get install python-scipy` (on debian/ubuntu)
 - opencv (optional): `sudo apt-get install python-opencv` (on debian/ubuntu)

##### Checkout + Compile

    git clone https://github.com/charun80/pyFLIF
    cd pyFLIF
    git submodule init
    git submodule update
    make

### Usage

#### Decoding

##### Simple method for single images

    import pyFLIF
    
    img = pyFLIF.imread( "path_to/image.flif" ) # numpy array with shape [ WxH(x3/4) ]

##### Advanced method also for animations


    import pyFLIF
    
    with pyFLIF.flifDecoder( "path_to/file.flif" ) as dec:
	    # decompressing all frames and storing them in a list
	    allframes = [ dec.getImage(idx) for idx in xrange(dec.numImages())
#### Encoding

##### Simple method for single images

    import pyFLIF
    
    # img: numpy array with shape [ WxH(x3/4 ]
    # dtype in (uint8, uint16)
    pyFLIF.imwrite( "path_to/image.flif", img ) 

##### Advanced method also for animations

    import pyFLIF
    
    with pyFLIF.flifEncoder( "path_to/file.flif" ) as enc:
	    for img in <image source>:
		    # all img shall have same shape [ WxH(x3/4) ] and dtype (uint8/uint16)
		    enc.addImage( img )]
