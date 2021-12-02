import os
import re
import sys
import subprocess
import pkgutil
from sysconfig import get_platform
from subprocess import CalledProcessError, check_output, check_call
from distutils.version import LooseVersion
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext

from pathlib import Path
from importlib.util import find_spec
addpaths = [Path(), ] 
sys.path[:0] = [str(path.absolute()) for path in addpaths]

import versioneer

# We can use cmake provided from pip which (normally) gets installed at /bin
# Except that in the manylinux builds it's placed at /opt/python/[version]/bin/
# (as a symlink at least) which is *not* on the path.
# If cmake is a known module, import it and use it tell us its binary directory
if pkgutil.find_loader('cmake') is not None:
    import cmake
    CMAKE_BIN = cmake.CMAKE_BIN_DIR + os.path.sep + 'cmake'
else:
    CMAKE_BIN = 'cmake'

def get_cmake():
    return CMAKE_BIN

# We want users to be able to specify the use of HDF5 for object IO.
# But this should not be turned on by default (yet).
# Enable HDF5 IO by passing `--use-hdf` when calling python setup.py.
USE_HDF5=False


def is_vsc():
    platform = get_platform()
    return platform.startswith("win")


def is_mingw():
    platform = get_platform()
    return platform.startswith("mingw")


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = check_output([get_cmake(), '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build" +
                               " the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        rex = r'version\s*([\d.]+)'
        cmake_version = LooseVersion(re.search(rex, out.decode()).group(1))
        if cmake_version < '3.13.0':
            raise RuntimeError("CMake >= 3.13.0 is required")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.dirname(self.get_ext_fullpath(ext.name))
        extdir = os.path.abspath(extdir)
        cmake_args = []
        if is_vsc():
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            else:
                cmake_args += ['-A', 'Win32']

        if is_mingw():
            cmake_args += ['-G','Unix Makefiles'] # Must be two entries to work

        cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                       '-DPython3_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        # cfg = 'Debug' if self.debug else 'RelWithDebInfo'
        build_args = ['--config', cfg, '--target', '_module']

        # make sure all library files end up in one place
        cmake_args += ["-DCMAKE_BUILD_WITH_INSTALL_RPATH=TRUE"]
        cmake_args += ["-DCMAKE_INSTALL_RPATH={}".format("$ORIGIN")]

        if is_vsc():
            cmake_lib_out_dir = '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'
            cmake_args += [cmake_lib_out_dir.format(cfg.upper(), extdir)]
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '/m:4']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j']

        env = os.environ.copy()
        cxxflags = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''), self.distribution.get_version())
        env['CXXFLAGS'] = cxxflags
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        check_call(
            [get_cmake(), ext.sourcedir] + cmake_args,
            cwd=self.build_temp, env=env)
        check_call(
            [get_cmake(), '--build', '.'] + build_args,
            cwd=self.build_temp)

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

KEYWORDARGS = dict(
    name='g5t-module',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(dict(build_ext=CMakeBuild)),
    author='Greg Tucker',
    author_email='gregory.tucker@ess.eu',
    description='Test Module.',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    ext_modules=[CMakeExtension('module._module')],
    options={'build': {'build_temp': 'cmake-build'}},
    packages=find_packages(),
    url="https://github.com/g5t/workflow",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ]
)

try:
    setup(**KEYWORDARGS)
except CalledProcessError:
    print("Failed to build the extension!")
