#!/bin/sh

JOBS=`nproc`

rm -rf build
mkdir build
cd build
../glibc/configure --disable-sanity-checks --disable-mathvec --disable-build-nscd --disable-nscd --disable-crypt --disable-werror --disable-multi-arch --disable-cet --disable-timezone-tools
make -j$JOBS |tee ../glibcmake.log
make -j$JOBS tests |tee ../glibctests.log
