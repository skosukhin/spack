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
import pytest
import subprocess
import os
from spack.util.module_cmd import get_path_from_module, \
    get_module_cmd_from_which
from spack.util.module_cmd import get_argument_from_module_line
from spack.util.module_cmd import get_module_cmd_from_bash
from spack.util.module_cmd import get_module_cmd, ModuleError


@pytest.fixture
def backup_restore_env():
    env_bu = os.environ.copy()

    yield

    os.environ.clear()
    os.environ.update(env_bu)


def run_bash_command(*args):
    return subprocess.Popen(
        ['/bin/bash'] + list(args),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    ).communicate()


def export_bash_function(name, body):
    out, _ = run_bash_command('-c', '%s () { %s; };export -f %s;env --null' %
                              (name, body, name))

    for var in out.strip('\0').split('\0'):
        var_name, var_value = var.split('=', 1)
        os.environ[var_name] = var_value


def unset_bash_function(name):
    out, _ = run_bash_command('-c', 'unset -f %s;env --null' % name)
    os.environ.clear()
    for var in out.strip('\0').split('\0'):
        var_name, var_value = var.split('=', 1)
        os.environ[var_name] = var_value


def create_bash_with_custom_init(path_to_dir, init_script=None,
                                 prepend_to_path=True):
    """Creates a wrapper for bash that ensures that system bash initialization
    scripts are ignored (except for the case of --posix). It also allows for
    initialization with a custom script but the implementation assumes that
    bash runs with -c argument. Not very robust but suits basic needs for
    testing.

    Parameters:
        path_to_dir(py.path.local): path to the directory, where the script
            will be stored.
        init_script(str): script that will be prepended to the bash
            command_string.
        prepend_to_path(bool): specifies whether or not the path to the script
            must be added to the PATH.

    """
    init_script = (init_script + ';') if init_script else ''
    path_to_bash = path_to_dir.join('bash')
    path_to_bash.write('#!/bin/bash\n'
                       'args=("--norc" "--noprofile")\n'
                       'for arg in "$@"; do\n'
                       '  case "$arg" in\n'
                       '    -*)\n'
                       '      new_arg="$arg";;\n'
                       '    *)\n'
                       '      new_arg="' + init_script + '$arg";;\n'
                       '  esac\n'
                       '  args=("${args[@]}" "$new_arg")\n'
                       'done\n'
                       'BASH_ENV= exec /bin/bash "${args[@]}"')
    path_to_bash.chmod(0o770)
    if prepend_to_path:
        if 'PATH' in os.environ:
            os.environ['PATH'] = str(path_to_dir) + ':' + os.environ['PATH']
        else:
            os.environ['PATH'] = str(path_to_dir)


def test_get_path_from_module(backup_restore_env, tmpdir):
    lines = ['prepend-path LD_LIBRARY_PATH /path/to/lib',
             'setenv MOD_DIR /path/to',
             'setenv LDFLAGS -Wl,-rpath/path/to/lib',
             'setenv LDFLAGS -L/path/to/lib',
             'prepend-path PATH /path/to/bin']

    create_bash_with_custom_init(tmpdir)

    for line in lines:
        export_bash_function('module', 'eval `echo ' + line + ' bash filler`')
        path = get_path_from_module('mod')

        assert path == '/path/to'

    export_bash_function('module', 'eval $(echo fill bash $*)')
    path = get_path_from_module('mod')

    assert path is None


def test_get_argument_from_module_line():
    lines = ['prepend-path LD_LIBRARY_PATH /lib/path',
             'prepend-path  LD_LIBRARY_PATH  /lib/path',
             "prepend_path('PATH' , '/lib/path')",
             'prepend_path( "PATH" , "/lib/path" )',
             'prepend_path("PATH",' + "'/lib/path')"]

    bad_lines = ['prepend_path(PATH,/lib/path)',
                 'prepend-path (LD_LIBRARY_PATH) /lib/path']

    assert all(get_argument_from_module_line(l) == '/lib/path' for l in lines)
    for bl in bad_lines:
        with pytest.raises(ValueError):
            get_argument_from_module_line(bl)


@pytest.mark.skipif(
    run_bash_command('-i', '-l', '-c', 'module avail; echo $?')[0] != '0\n',
    reason='Depends on defined module command')
def test_get_module_cmd_from_bash_using_modules(tmpdir):
    with tmpdir.as_cwd():
        # Bash initialization scripts might report on errors but we want
        # only pure stderr of the command, which is why we redirect its output
        # to a file.
        run_bash_command('-i', '-l', '-c', 'module list 2> module_list.txt')
        with open('module_list.txt') as f:
            module_list = f.read()

    module_cmd = get_module_cmd()
    module_cmd_list = module_cmd('list', output=str, error=str)

    # Lmod command reprints some env variables on every invocation.
    # Test containment to avoid false failures on lmod systems.
    assert module_list in module_cmd_list


def test_get_module_cmd_from_bash_ticks(backup_restore_env, tmpdir):
    export_bash_function('module', 'eval `echo bash $*`')

    create_bash_with_custom_init(tmpdir)

    module_cmd = get_module_cmd_from_bash()
    module_cmd_list = module_cmd('list', output=str, error=str)

    assert module_cmd_list == 'python list\n'


def test_get_module_cmd_from_bash_parens(backup_restore_env, tmpdir):
    export_bash_function('module', 'eval $(echo fill sh $*)')

    create_bash_with_custom_init(tmpdir)

    module_cmd = get_module_cmd_from_bash()
    module_cmd_list = module_cmd('list', output=str, error=str)

    assert module_cmd_list == 'fill python list\n'


def test_get_module_cmd_from_bash_with_shell_var(backup_restore_env, tmpdir):
    bash_function = 'eval `$ECHO bash $*`'
    export_bash_function('module', bash_function)

    create_bash_with_custom_init(tmpdir)

    with pytest.raises(ModuleError) as e:
        get_module_cmd_from_bash()
    assert \
        'Failed to create executable based on shell function \'module\'.' == \
        e.value.message

    create_bash_with_custom_init(tmpdir, 'ECHO=echo')

    module_cmd = get_module_cmd_from_bash()
    module_cmd_list = module_cmd('list', output=str, error=str)

    assert module_cmd_list == 'python list\n'


def test_get_module_cmd_fails(backup_restore_env, tmpdir):
    unset_bash_function('module')

    create_bash_with_custom_init(tmpdir)

    with pytest.raises(ModuleError) as e:
        get_module_cmd_from_bash()
    assert 'Bash function \'module\' is not defined.' == e.value.message

    # Only bash wrapper is in the PATH
    os.environ['PATH'] = str(tmpdir)

    with pytest.raises(ModuleError) as e:
        get_module_cmd_from_which()
    assert '`which` did not find any modulecmd executable' == e.value.message

    with pytest.raises(ModuleError) as e:
        get_module_cmd()
    assert e.value.message.startswith('Spack requires modulecmd or a defined ')


def test_get_module_cmd_from_which(backup_restore_env, tmpdir):
    f = tmpdir.join('modulecmd')
    f.write('#!/bin/bash\n'
            'echo $*')
    f.chmod(0o770)

    os.environ['PATH'] = str(tmpdir) + ':' + os.environ['PATH']

    module_cmd = get_module_cmd_from_which()
    module_cmd_list = module_cmd('list', output=str, error=str)

    assert module_cmd_list == 'python list\n'
