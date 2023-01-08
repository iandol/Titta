# to build, run python -m pip wheel .
# to install, run python -m pip install .
# add -v switch to see output during build

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys

# detect platform
if sys.platform.startswith("win"):
    plat = "win"
elif sys.platform.startswith("linux"):
    plat = "linux"
elif sys.platform.startswith("darwin"):
    plat = "osx"

__version__ = '1.0.0rc1'

# dll to install along with built module
if plat=="win":
    data_files = [('lib\\site-packages\\',["./SDK_wrappper/64/Windows/tobii_research.dll"])]
elif plat=="linux":
    data_files = [('lib\\site-packages\\',["./SDK_wrappper/64/Linux/libtobii_research.so.1.10.1"])]
elif plat=="osx":
    data_files = [('lib\\site-packages\\',["./SDK_wrappper/64/Linux/libtobii_research.1.10.1.dylib"])]


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path

    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)


ext_modules = [
    Extension(
        'TittaPy',
        ['src/Titta.cpp','src/types.cpp','src/utils.cpp','TittaPy/TittaPy.cpp'],
        include_dirs=[
            # Path to pybind11 headers
            get_pybind_include(),
            get_pybind_include(user=True),
            '.',
            'deps/include'
        ],
        library_dirs=[
            'deps/lib'
            ],
        language='c++'
    ),
]


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/DBUILD_FROM_SCRIPT','/DNDEBUG','/Zp8','/GR','/W3','/EHs','/nologo','/MD','/std:c++latest','/Gy','/Oi','/GL','/permissive-','/O2'],
        'unix': ['-DBUILD_FROM_SCRIPT','-DNDEBUG','-std=c++2a','-O3','-fvisibility=hidden','-ffunction-sections','-fdata-sections','-flto '],
    }
    l_opts = {
        'msvc': ['/LTCG','/OPT:REF','/OPT:ICF'],
        'unix': ['-Wl,--gc-sections -flto'],
    }
    if plat=="osx":
        l_opts['unix'].append('-Wl,-rpath,''@loader_path''')
    else:
        l_opts['unix'].append('-Wl,-rpath,''$ORIGIN''')

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO="%s"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)

setup(
    name='TittaPy',
    version=__version__,
    author='Diederick C. Niehorster',
    author_email='diederick_c.niehorster@humlab.lu.se',
    url='https://github.com/dcnieho/Titta',
    description='Interface to Tobii eye trackers using Tobii Pro SDK',
    keywords="Tobii PsychoPy",
    long_description='',
    ext_modules=ext_modules,
    python_requires=">=3.8",
    setup_requires=['pybind11>=2.10.1'],  # this fixes problem if c++23 std::forward_like is available that i ran into
    cmdclass={'build_ext': BuildExt},
    data_files=data_files
)