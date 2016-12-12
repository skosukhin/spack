"""This module contains classes that represent parts of the Cray Linux
Environment (CLE)."""
import re
import os

from spack.architecture import OperatingSystem
from spack.operating_systems.linux_distro import LinuxDistro
from spack.util.executable import *
import spack.spec
from spack.util.multiproc import parmap
import spack.compilers


class Cnl(OperatingSystem):
    """ Compute Node Linux (CNL) is the operating system used for the Cray XC
    series super computers. It is a very stripped down version of GNU/Linux.
    Any compilers found through this operating system will be used with
    modules. If updated, user must make sure that version and name are
    updated to indicate that OS has been upgraded (or downgraded)
    """

    def __init__(self):
        name = 'CNL'
        version = '10'
        super(Cnl, self).__init__(name, version)

    def __str__(self):
        return self.name

    def find_compilers(self, *paths):
        types = spack.compilers.all_compiler_types()
        compiler_lists = parmap(
            lambda cmp_cls: self.find_compiler(cmp_cls, *paths), types)

        # ensure all the version calls we made are cached in the parent
        # process, as well.  This speeds up Spack a lot.
        clist = reduce(lambda x, y: x + y, compiler_lists)
        return clist

    def find_compiler(self, cmp_cls, *paths):
        compilers = []
        if cmp_cls.PrgEnv:
            if not cmp_cls.PrgEnv_compiler:
                tty.die('Must supply PrgEnv_compiler with PrgEnv')

            modulecmd = which('modulecmd')
            modulecmd.add_default_arg('python')

            # Save the environment variable to restore later
            old_modulepath = os.environ['MODULEPATH']
            # if given any explicit paths, search them for module files too
            if paths:
                module_paths = ':' + ':'.join(p for p in paths)
                os.environ['MODULEPATH'] = module_paths

            output = modulecmd(
                'avail', cmp_cls.PrgEnv_compiler, output=str, error=str)
            matches = re.findall(
                r'(%s)/([\d\.]+[\d])' % cmp_cls.PrgEnv_compiler, output)
            for name, version in matches:
                v = version
                comp = cmp_cls(
                    spack.spec.CompilerSpec(name + '@' + v),
                    self, any,
                    ['cc', 'CC', 'ftn'], [cmp_cls.PrgEnv, name + '/' + v])

                compilers.append(comp)

            # Restore modulepath environment variable
            if paths:
                os.environ['MODULEPATH'] = old_modulepath

        return compilers


class CrayFrontend(LinuxDistro):
    """The class represents the OS that runs on login and service nodes of the
    Cray platform. It acts as a regular Linux without Cray-specific modules and
    compiler wrappers."""

    _modulecmd = which('modulecmd', required=True)
    _modulecmd.add_default_arg('python')

    def find_compilers(self, *paths):
        """Calls the overridden method but prevents it from detecting Cray
        compiler wrappers by disabling them. There are two reasons for that:
        first of all, we avoid possible false detection of the compiler wrappers
        (e.g. if PrgEnv-intel module is loaded the algorithm identifies the
        wrappers as Cray compilers but not Intel, since the version string
        returned by Intel compilers is acceptable by Cray compilers' regexp);
        second, we do not need them anyway, since this class should come into
        play only if a user, by whatever reason, decides to work with the
        frontend OS as if it was a regular Linux environment without
        Cray-specific modules and wrappers."""

        # If $PE_ENV is set then one of the PrgEnv-* modules is loaded.
        prg_env = ('PrgEnv-' + os.environ['PE_ENV'].lower()
                   if 'PE_ENV' in os.environ
                   else None)

        if prg_env:
            unload_script =\
                self._modulecmd('unload', prg_env, output=str, error=os.devnull)
            exec (compile(unload_script, '<string>', 'exec'))

        clist = super(CrayFrontend, self).find_compilers(*paths)

        if prg_env:
            load_script =\
                self._modulecmd('load', prg_env, output=str, error=os.devnull)
            exec (compile(load_script, '<string>', 'exec'))

        return clist
