import re
import os

from spack.architecture import OperatingSystem
from spack.operating_systems.linux_distro import LinuxDistro
from spack.util.executable import *
import spack.spec
from spack.util.multiproc import parmap
import spack.compilers


class CrayFrontend(LinuxDistro):
    """
    The class represents the frontend OS of the Cray platform. It can be used
    if a user, for whatever reason, decides to work with the frontend OS as it
    was a regular Linux environment without Cray specific modules and wrappers.
    """

    def find_compilers(self, *paths):
        # Unset PE_ENV to avoid detection of Cray compiler wrappers. If we do
        # not do so, there is a chance for an error in the following compiler
        # detection algorithm. For example, if the module PrgEnv-intel is
        # loaded the algorithm identifies Cray's compiler wrappers as Cray
        # compilers but not Intel.

        pe_env_val = os.environ['PE_ENV'] if 'PE_ENV' in os.environ else None

        if pe_env_val:
            del os.environ['PE_ENV']

        clist = super(CrayFrontend, self).find_compilers(*paths)

        if pe_env_val:
            os.environ['PE_ENV'] = pe_env_val

        return clist


class CrayOS(OperatingSystem):
    """
    The class represents Cray OS, all the compilers that are detected come from
    the standard Cray modules. Depending on the specified target, a user can
    also compile software for frontend nodes.
    """

    modulecmd = which('modulecmd')
    modulecmd.add_default_arg('python')

    def __init__(self):
        name = 'CLE'  # Cray Linux Environment
        version = os.environ['CRAYOS_VERSION']
        super(CrayOS, self).__init__(name, version)

    def find_compilers(self, *paths):
        """
        The interface method that finds compilers that are available in the
        system.
        :param paths: The parameter is ignored.
        """
        return self.find_compilers_in_modules()

    def find_compilers_in_modules(self, modulepaths=None,
                                  replace_modpath=False):
        """
        The method detects compilers that are available through the environment
        module system.
        :param modulepaths: List of paths that replace or are appended to the
        environment variable MODULEPATH.
        :param replace_modpath: Flag that indicates if the provided list of
        modpaths should replace (True) or be appended to the value of the
        environment variable MODULEPATH. If modpaths is None then this
        parameter is ignored.
        """
        mod_list = CrayOS.get_avail_modules(modulepaths, replace_modpath)

        types = spack.compilers.all_compiler_types()
        compiler_lists = parmap(
            lambda cmp_cls: self.find_compiler_in_mod_list(cmp_cls, mod_list),
            types)

        # ensure all the version calls we made are cached in the parent
        # process, as well.  This speeds up Spack a lot.
        clist = reduce(lambda x, y: x + y, compiler_lists)
        return clist

    def find_compiler_in_mod_list(self, cmp_cls, mod_list):
        """
        The method detects if the specified compiler presents in the provided
        list of modules.
        :param cmp_cls: Compiler module that the method checks for
        availability.
        :param mod_list: List of modules.
        """

        compilers = []
        if cmp_cls.PrgEnv:
            if not cmp_cls.PrgEnv_compiler:
                tty.die('Must supply PrgEnv_compiler with PrgEnv')

            # We should check if the corresponding compiler suite is available
            # in the system. We only use the default versions of them.
            comp_suite_mods = re.findall(r'^%s/' % cmp_cls.PrgEnv, mod_list,
                                         flags=re.M)

            if len(comp_suite_mods) > 0:
                comp_mods = re.findall(
                    r'^%s/([\d.]+)' % cmp_cls.PrgEnv_compiler, mod_list,
                    flags=re.M)

                for version in comp_mods:
                    comp = cmp_cls(spack.spec.CompilerSpec(
                        cmp_cls.PrgEnv_compiler + '@' + version),
                        self,
                        ['cc', 'CC', 'ftn'],
                        [cmp_cls.PrgEnv,
                         cmp_cls.PrgEnv_compiler + '/' + version])

                    compilers.append(comp)

        return compilers

    @staticmethod
    def get_avail_modules(modulepaths=None, replace_modpath=False):
        """
        The method returns a list of modules that are available in the system.
        :param modulepaths: List of paths that replace or are appended to the
        environment variable MODULEPATH.
        :param replace_modpath: Flag that indicates if the provided list of
        modpaths should replace (True) or be appended to the value of the
        environment variable MODULEPATH. If modpaths is None then this
        parameter is ignored.
        """

        env = os.environ.copy()
        if modulepaths:
            new_modulepath = ':'.join(p for p in modulepaths)
            if replace_modpath:
                env['MODULEPATH'] = new_modulepath
            elif len(modulepaths) > 0:
                env['MODULEPATH'] += ':' + new_modulepath

        output = CrayOS.modulecmd(
            'avail',
            '-t',
            output=os.devnull,
            error=str,
            env=env)

        return output
