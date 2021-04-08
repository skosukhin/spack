from spack.directives import variant
from spack.package import PackageBase


def mpi_launch_values(x):
    """Pretty string describing possible values for mpi_launched
    """
    # The docstring above is used for the 'spack info' output.
    return x


class MPIRunnerPackage(PackageBase):
    variant('mpi_launch', default='none', values=mpi_launch_values,
            description='MPI launcher command')
