##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os

class Oifs(Package):
    """The OpenIFS programme at ECMWF aims to encourage research and teaching into numerical weather prediction from medium range to seasonal timescales.
       We provide academic and research institutions with an easy-to-use version of ECMWF IFS (Integrated Forecasting System) (the OpenIFS model), the 
       single column model (SCM) and the offline-surface model (OSM). The OpenIFS model provides the full forecast capability of IFS, supporting software 
       and documentation but without the data assimilation system. OpenIFS is a global model."""

    homepage = "https://software.ecmwf.int/wiki/display/OIFS"
    url      = "http://www.bsc.es/projects/earthscience/public/kserradell/files/oifs40r1.tar.gz"

    version('40r1', '5e55122d2bc7e175af931efeded06e83')

    depends_on('openmpi',type=('build','run','link'))
    depends_on('grib-api',type=('build','run','link'))
    depends_on('openblas',type=('build','run','link'))

    def install(self, spec, prefix):

    	# Defining installation
    	os.environ['OIFS_COMP'] = 'spack'
    	os.environ['OIFS_BUILD'] = 'opt'

        # Clean previous installation (if any)
        os.system('rm -rf ' + os.getcwd() + '/make/spack-opt/')
        os.system('rm -rf ' + os.getcwd() + '/make/cfg/spack-opt.cfg')

        # GNU compilation
        if self.compiler.name == 'gcc':
         	with open(os.getcwd() + '/make/cfg/spack-opt.cfg', 'w') as f:
	            f.writelines([
				 '$OIFS_GRIB_API_DIR{?}     = ' +  spec['grib-api'].prefix + '\n'
				 '$OIFS_GRIB_API_INCLUDE{?} = -I $OIFS_GRIB_API_DIR/include\n'
				 '$OIFS_GRIB_API_LIB{?}     = -L$OIFS_GRIB_API_DIR/lib -lgrib_api_f90 -lgrib_api\n'
				 '\n'
				 '# LAPACK & BLAS libraries\n'
				 '$LAPACK_LIB_DEFAULT = -L' +  spec['openblas'].prefix.lib + ' -lopenblas\n'
				 '\n'
				 '# Extra libraries (architecture/compiler specific)\n'
 				 '$OIFS_EXTRA_LIB{?}  = \n'
 				 '\n'
 				 '# Source files that FCM should specifically ignore\n'
 				 '$SRC_EXCL = \n'
 				 '\n'		
				 '# Fortran\n'
				 '$OIFS_FC{?}     = mpif90\n'
				 '$OIFS_FFLAGS{?} = -g -O2 -m64 -fconvert=big-endian -fopenmp\n'
				 '$OIFS_FFIXED{?} = -fdefault-real-8 -fdefault-double-8 -ffixed-line-length-132\n'
				 '$OIFS_FCDEFS{?} = BLAS LITTLE LINUX INTEGER_IS_INT F90 PARAL NONCRAYF\n'
				 '$OIFS_LFLAGS{?} = -fopenmp\n'
				 '\n'
				 '# C compiler\n'
				 '$OIFS_CC{?}     = mpicc\n'
				 '$OIFS_CFLAGS{?} = -g -O -m64\n'
				 '$OIFS_CCDEFS{?} = BLAS LITTLE LINUX INTEGER_IS_INT _ABI64\n'
				 '\n'		
	            ])
        # INTEL compilation
        elif self.compiler.name == 'intel':
         	with open(os.getcwd() + '/make/cfg/spack-opt.cfg', 'w') as f:	
	            f.writelines([
				 '$OIFS_GRIB_API_DIR{?}     = ' +  spec['grib-api'].prefix + '\n'
				 '$OIFS_GRIB_API_INCLUDE{?} = -I $OIFS_GRIB_API_DIR/include\n'
				 '$OIFS_GRIB_API_LIB{?}     = -L$OIFS_GRIB_API_DIR/lib -lgrib_api_f90 -lgrib_api\n'
				 '\n'
				 '# LAPACK & BLAS libraries\n'
				 '$LAPACK_LIB_DEFAULT = -L' +  spec['openblas'].prefix.lib + ' -lopenblas\n'
				 '\n'
				 '# Extra libraries (architecture/compiler specific)\n'
 				 '$OIFS_EXTRA_LIB{?}  = \n'
 				 '\n'
 				 '# Source files that FCM should specifically ignore\n'
 				 '$SRC_EXCL = \n'
 				 '\n'					
				 '# Fortran\n'
				 '$OIFS_FC{?}     = mpif90\n'
				 '$OIFS_FFLAGS{?} = -g -m64 -openmp -O1 -xHost -fp-model precise -convert big_endian -traceback\n'
				 '$OIFS_FFIXED{?} = -r8\n'
				 '$OIFS_FCDEFS{?} = BLAS LITTLE LINUX INTEGER_IS_INT\n'
				 '$OIFS_LFLAGS{?} = -openmp\n'
				 '\n'
				 '# C compiler\n'
				 '\n'
				 '$OIFS_CC{?}     = mpicc\n'
				 '$OIFS_CFLAGS{?} = -g -O\n'
				 'OIFS_CCDEFS{?} = BLAS LITTLE LINUX INTEGER_IS_INT _ABI64\n'
	            ])        	

        # Change directory to make
        os.chdir(os.getcwd() + '/make/')

        # Execute fcm build command
        ncpus = os.sysconf("SC_NPROCESSORS_ONLN")
        os.system('../fcm/bin/fcm make -j ' + str(ncpus) + ' -v -f oifs.cfg')
  
        # Add bin to spack package
        install_tree(os.getcwd() + '/spack-opt/oifs/bin/', prefix.bin)