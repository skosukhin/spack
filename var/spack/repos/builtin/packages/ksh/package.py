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


class Ksh(Package):
    """KornShell (ksh) is a Unix shell which was developed by David Korn at
    Bell Labs. KornShell is backward-compatible with the Bourne shell and
    includes many features of the C shell, inspired by the requests of Bell
    Labs users."""

    homepage = 'http://www.kornshell.com'
    url = 'https://github.com/att/ast'

    version('master', git='https://github.com/att/ast', branch='master')

    depends_on('coreutils', type='build')
    depends_on('meson+ninjabuild', type='build')

    def install(self, spec, prefix):
        meson = which('meson')
        meson('build')
        ninja('-C', 'build')
