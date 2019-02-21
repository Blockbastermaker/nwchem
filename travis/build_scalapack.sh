#!/bin/bash 
source $TRAVIS_BUILD_DIR/travis/nwchem.bashrc
if [[ "$USE_64TO32" != "y" ]] ; then exit 0; fi
cd $TRAVIS_BUILD_DIR
os=`uname`
svn co  https://icl.utk.edu/svn/scalapack-dev/scalapack/trunk/ scalapack
#git clone https://github.com/scibuilder/scalapack.git
#git clone https://github.com/edoapra/scalapack.git 
mkdir -p scalapack/build
cd scalapack/build
cmake -Wno-dev ../ -DCMAKE_BUILD_TYPE=RelWithDebInfo -DTEST_SCALAPACK=OFF  -DBUILD_TESTING=OFF -DBUILD_SHARED_LIBS=ON  -DBLAS_blas_LIBRARY="-L$TRAVIS_BUILD_DIR -lopenblas" -DLAPACK_lapack_LIBRARY="-L$TRAVIS_BUILD_DIR  -lopenblas"  -DCMAKE_INSTALL_PREFIX=$TRAVIS_BUILD_DIR
$TRAVIS_BUILD_DIR/travis/sleep_loop.sh make V=0 -j3 
make V=0 install -j3
if [[ "$os" == "Darwin" ]]; then 
    cd $TRAVIS_BUILD_DIR/lib
    install_name_tool -id $TRAVIS_BUILD_DIR/lib/libscalapack.dylib  libscalapack.dylib
    otool -L $TRAVIS_BUILD_DIR/lib/libscalapack.dylib
fi
if [[ "$os" == "Linux" ]]; then 
    ldd $TRAVIS_BUILD_DIR/lib/libscalapack.so
fi
