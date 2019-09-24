#!/bin/bash
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then 
  brew cask uninstall oclint || true  
  brew install gcc "$MPI_IMPL" openblas ||true
  if [[ "$MPI_IMPL" == "openmpi" ]]; then
     brew install scalapack
  fi
fi
if [[ "$TRAVIS_OS_NAME" == "linux" ]]; then 
    if [[ "$MPI_IMPL" == "openmpi" ]]; then
	mpi_bin="openmpi-bin" ; mpi_libdev="libopenmpi-dev" scalapack_libdev="libscalapack-openmpi-dev"
    fi
    if [[ "$MPI_IMPL" == "mpich" ]]; then
        mpi_bin="mpich" ; mpi_libdev="libmpich-dev" scalapack_libdev="libscalapack-mpich-dev"
    fi
    cat /etc/apt/sources.list
    sudo add-apt-repository universe && sudo apt update
    sudo apt-get -y install gfortran python-dev  cmake "$mpi_libdev" "$mpi_bin" "$scalapack_libdev" tcsh make perl subversion libopenblas-dev 
fi