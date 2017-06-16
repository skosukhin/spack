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


class Oifs(Package):
    """The OpenIFS programme at ECMWF aims to encourage research and teaching into numerical weather prediction from medium range to seasonal timescales.
       We provide academic and research institutions with an easy-to-use version of ECMWF IFS (Integrated Forecasting System) (the OpenIFS model), the 
       single column model (SCM) and the offline-surface model (OSM). The OpenIFS model provides the full forecast capability of IFS, supporting software 
       and documentation but without the data assimilation system. OpenIFS is a global model."""

    homepage = "https://software.ecmwf.int/wiki/display/OIFS"
    url      = "http://www.bsc.es/projects/earthscience/public/kserradell/files/oifs40r1.tar.gz"

    version('40r1', '5e55122d2bc7e175af931efeded06e83')

    depends_on('openmpi')
    depends_on('grib-api')
    depends_on('openblas')

    def setup_environment(self, spack_env, run_env):
        run_env.set('OIFS_COM', 'gnu')
        run_env.set('OIFS_BUILD', 'opt')

    def edit(self, spec, prefix):
        run_env.prepend_path('PATH', os.getcwd() + '/fcm/bin')
        # Modify arch file
        # add grib-api path 
        # add openblas path
    
    def install(self, spec, prefix):
        # Execute fcm command (fcm make -v -f oifs.cfg)
        make()



