##############################################################################
# Copyright (c) 2013-2017, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/spack/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
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


class Xdbedizzy(AutotoolsPackage):
    """xdbedizzy is a demo of the X11 Double Buffer Extension (DBE)
    creating a double buffered spinning scene."""

    homepage = "http://cgit.freedesktop.org/xorg/app/xdbedizzy"
    url      = "https://www.x.org/archive/individual/app/xdbedizzy-1.1.0.tar.gz"

    version('1.1.0', '969be2f6bc62455431ab027f99720dc3')

    depends_on('libx11')
    depends_on('libxext')

    depends_on('pkg-config@0.9.0:', type='build')
    depends_on('util-macros', type='build')
