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
    """The OpenIFS programme at ECMWF aims to encourage research and teaching
        into numerical weather prediction from medium range to seasonal
        timescales. We provide academic and research institutions with an
        easy-to-use version of ECMWF IFS (Integrated Forecasting System) (the
        OpenIFS model), the single column model (SCM) and the offline-surface
        model (OSM). The OpenIFS model provides the full forecast capability
        of IFS, supporting software and documentation but without the data
        assimilation system. OpenIFS is a global model."""

    homepage = "https://software.ecmwf.int/wiki/display/OIFS"
    url = "http://www.bsc.es/projects/earthscience/public/kserradell/files/oifs40r1.tar.gz"

    version('40r1', '5e55122d2bc7e175af931efeded06e83')

    depends_on('mpi')
    depends_on('grib-api')
    depends_on('lapack')

    # Starting the version 5.10, Perl's core contains Time::Piece, which is
    # necessary to run FCM. Keep in mind that some Linux distributions provide
    # Perl packages without core modules, so better not specify Perl as an
    # external package but always build it with Spack.
    depends_on('perl@5.10:', type='build')

    def install(self, spec, prefix):

        # Fortran flags
        f_flags = ['-g', '-m64']
        f_fixed = []
        f_cdefs = ['BLAS', 'LITTLE', 'LINUX', 'INTEGER_IS_INT']

        # C flags
        c_flags = ['-g', '-O']
        c_cdefs = ['BLAS', 'LITTLE', 'LINUX', 'INTEGER_IS_INT', '_ABI64']

        # Linker flags
        l_flags = []

        if self.spec.satisfies('%gcc'):
            f_flags.extend(['-O2', '-fconvert=big-endian'])
            f_fixed.extend(['-fdefault-real-8', '-fdefault-double-8',
                            '-ffixed-line-length-132'])
            f_cdefs.extend(['F90', 'PARAL', 'NONCRAYF'])
            c_flags.extend(['-m64'])
        elif self.spec.satisfies('%intel'):
            f_flags.extend(['-O1', '-xHost', '-fp-model precise',
                            '-convert big_endian', '-traceback'])
            f_fixed.extend(['-r8'])
        else:
            raise InstallError('Only GNU and Intel compilers are supported.')

        f_flags.append(self.compiler.openmp_flag)
        l_flags.append(self.compiler.openmp_flag)

        with open('make/cfg/spack-opt.cfg', 'w') as f:
            f.writelines([
                # Spack's compiler wrapper will add -I and -L flags, so we
                # don't have to put them in the file.

                '$OIFS_FC = ' + self.spec['mpi'].mpifc + '\n',
                '$OIFS_FFLAGS = ' + ' '.join(f_flags) + '\n',
                '$OIFS_FFIXED = ' + ' '.join(f_fixed) + '\n',
                '$OIFS_FCDEFS = ' + ' '.join(f_cdefs) + '\n',

                '$OIFS_CC = ' + self.spec['mpi'].mpicc + '\n',
                '$OIFS_CFLAGS = ' + ' '.join(c_flags) + '\n',
                '$OIFS_CCDEFS = ' + ' '.join(c_cdefs) + '\n',

                '$OIFS_LFLAGS = ' + ' '.join(l_flags) + '\n',

                '$OIFS_GRIB_API_LIB = -lgrib_api_f90 -lgrib_api\n',

                '$LAPACK_LIB_DEFAULT = ' +
                self.spec['lapack'].libs.link_flags + '\n',

                # Declaration of empty but mandatory variables:
                '$OIFS_GRIB_API_INCLUDE =\n',
                '$SRC_EXCL =\n',
                '$OIFS_EXTRA_LIB =\n'
            ])

        oifs_cfg = join_path(self.stage.source_path, 'make/oifs.cfg')

        # Remove '{?}' from the variable definitions in oifs.cfg to make sure
        # they won't be overridden by environment variables (except for
        # OIFS_COMP and OIFS_BUILD, which we set ourselves).
        filter_file(r'^(\$(?!OIFS_COMP|OIFS_BUILD)\w+)\{\?\}(\s*=.*)$',
                    r'\1\2', oifs_cfg)

        fcm = Executable(join_path(self.stage.source_path, 'fcm/bin/fcm'))
        fcm.add_default_env('OIFS_COMP', 'spack')
        fcm.add_default_env('OIFS_BUILD', 'opt')

        with working_dir('make'):
            # Delete fcm lock (if it exists) to continue interrupted building.
            rmtree('spack-opt/fcm-make.lock', ignore_errors=True)
            fcm('make', '-j', str(make_jobs), '-v', '-f', oifs_cfg)
            install_tree('spack-opt/oifs/bin', prefix.bin)
