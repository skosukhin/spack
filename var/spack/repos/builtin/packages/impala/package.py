# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Impala(CMakePackage):
    """Impala is an imperative and functional programming language which targets
    the Thorin intermediate representation. Its syntax heavily borrows from
    Rust, with some noticeable changes: It allows user-directed partial
    evaluation of code and continuation-passing style (CPS)."""

    homepage = 'https://anydsl.github.io/Impala'
    git = 'https://github.com/AnyDSL/impala.git'

    maintainers = ['skosukhin']

    version('master', branch='master')

    variant('build_type', default='Release', description='CMake build type',
            values=('Debug', 'Release'))

    depends_on('thorin')

    # def cmake_args(self):
    #     args = []
    #     return args
