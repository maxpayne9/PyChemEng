#!/usr/bin/env python
"""Build script for PyChemEng.

Added automatic fetching/building of pyOpt (>=1.2.0) so users do not
need to pre-install it manually. NOTE: pyOpt 1.2.0 requires Python >=3.7.
The current Cython sources use language_level=2 (Python 2 semantics);
to use bundled pyOpt you must run this build under Python 3.7+ and
incrementally port the codebase (e.g. update print statements) or set
cython language_level=3. If you must stay on Python 2, pin an older
pyOpt (unsupported) or replace pyOpt usage with an alternative SLSQP
solver (e.g. scipy.optimize.minimize).
"""

from setuptools import setup, Extension
from Cython.Distutils import build_ext
import os
import io

# Helper to read README for long_description
here = os.path.abspath(os.path.dirname(__file__))
def _read(fname):
    try:
        with io.open(os.path.join(here, fname), 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        return ''

ext_modules = [Extension('chemeng.elementdata', ['src/chemeng/elementdata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.NASAdata', ['src/chemeng/NASAdata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.cementdata', ['src/chemeng/cementdata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.chemkindata', ['src/chemeng/chemkindata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.speciesdata', ['src/chemeng/speciesdata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.antoinedata', ['src/chemeng/antoinedata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.transportdata', ['src/chemeng/transportdata.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.components', ['src/chemeng/components.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.ponchonsavarit', ['src/chemeng/PonchonSavarit.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.phase', ['src/chemeng/phase.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.standarddefinitions', ['src/chemeng/standarddefinitions.pyx'], language='c++', include_dirs=['.']),
               Extension('chemeng.entropymaximiser', ['src/chemeng/entropymaximiser.pyx'], language='c++', include_dirs=['.']),
               ]

setup(
    name="chemeng",
    version="0.1dev",
    author="M. Campbell Bannerman",
    author_email="m.bannerman@gmail.com",
    description="Chemical engineering thermodynamics & equilibrium (with cement/mineral data)",
    long_description=_read('README.md'),
    long_description_content_type='text/markdown',
    url="https://github.com/maxpayne9/PyChemEng",
    # Bundle vendored pyOpt (Python 2.7 compatible fork/legacy) located at src/pyOpt-1.2.0/pyOpt
    packages=['chemeng','pyOpt'],
    package_dir={'chemeng':'src/chemeng', 'pyOpt':'src/pyOpt-1.2.0/pyOpt'},
    package_data={'chemeng' : ['data/antoine.inp',
                               'data/mass.mas03round.txt',
                               'data/isotopicCompositions.inp',
                               'data/NASA_CEA.inp',
                               'data/NEWNASA.TXT',
                               'data/Cement.csv',
                               'data/Cement2.csv',
                               'data/BurcatCHEMKIN.DAT',
                               'data/NistData.csv',
                               'data/Cement_New_Tests.csv',
                               'data/Cement_Therm_New2.csv'
                           ]},
    cmdclass = {'build_ext': build_ext},
    py_modules = ['chemeng.config'],
    ext_modules = ext_modules,
    install_requires=[
        'Cython>=0.28',
        'numpy>=1.7.0,<1.17'  # Range friendly to Python 2.7 & legacy pyOpt
    ],
    # Keep Python 2.7 compatibility (user requested); no python_requires to avoid pip rejection.
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry'
    ],
    license='MIT'
)
