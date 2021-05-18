# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Thorin(CMakePackage):
    """Thorin is an intermediate representation based on continuation-passing
    style (CPS). Thorin embraces the sea-of-nodes paradigm. This means that each
    value is represented as node a graph."""

    homepage = 'https://anydsl.github.io/Thorin'
    git = 'https://github.com/AnyDSL/thorin.git'

    maintainers = ['skosukhin']

    version('master', branch='master')

    variant('build_type', default='Release', description='CMake build type',
            values=('Debug', 'Release'))

    depends_on('half', type='build')

    # FIXME: Add dependencies if required.
    # depends_on('foo')

    # def cmake_args(self):
    #     args = []
    #     return args

    def install(self, spec, prefix):
        """TODO: add install commands upstream"""
        with working_dir(self.build_directory):
            install_tree('include', prefix.include)
            install_tree('lib', prefix.lib)
            install_tree('share/anydsl/cmake', prefix.share.thorin.cmake)
