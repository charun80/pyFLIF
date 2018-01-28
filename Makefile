

LIBEXT = .so
OSNAME := $(shell uname -s)
ifeq ($(OSNAME),Darwin)
  LIBEXT = .dylib
endif

all:
	cd FLIF/src && $(MAKE) libflif$(LIBEXT)

clean:
	cd FLIF/src && $(MAKE) clean

