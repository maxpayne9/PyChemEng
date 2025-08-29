PyChemEng
=========

PyChemEng is a (Cython‑accelerated) toolkit for performing classical chemical engineering thermodynamic and reaction equilibrium calculations. It provides:

* Species & phase thermodynamic property evaluation (Cp, H, S, G, etc.)
* Mixture & phase abstractions (ideal gas, incompressible/solid/liquid)
* Elemental and species balance based equilibrium (free energy / entropy driven) via SLSQP (pyOpt)
* Cement & high‑temperature mineral datasets (multiple polynomial forms) for clinker phase exploration

Quick Start
-----------
```python
from chemeng import *
import chemeng.cementdata  # load cement & mineral species

air = Components({'O2':0.21,'N2':0.79})
fuel = Components({'CH4':1.0})
elem = fuel.elementalComposition()
reqO2 = elem['C'] + elem['H']/4.0
mix = fuel + air * (reqO2/air['O2'])

phase = IdealGasPhase(mix + Components({'CO2':0,'H2O':0,'CO':0,'OH':0,'O':0,'H':0,'NO':0}), T=298.15, P=1e5)
flame = findEquilibrium([phase], constP=True, constH=True, elemental=True)[0]
print "Adiabatic flame temperature (K):", flame.T
```

Comprehensive Manual
--------------------
A detailed manual (architecture, APIs, thermodynamic models, cement/mineral data layer usage, examples) is available in: `doc/PyChemEng_Manual.md`.

Legacy Online Docs
------------------
[Archived original documentation](http://toastedcrumpets.github.io/PyChemEng/) (may be outdated vs. this manual).

Testing
-------
Run the bundled regression / sanity checks:
```bash
python Test.py
python selftest.py  # fast automated sanity suite (JSON summary)
```

Acknowledgements
----------------
Authored by Theodore Hanein and Marcus N. Bannerman.

* NASA CEA (thermo.inp / trans.inp) data: NASA Glenn Research Center – http://www.grc.nasa.gov/WWW/CEAWeb/
* Reaction equilibrium test comparisons: GasEq – http://www.gaseq.co.uk/
* Cement & mineral thermodynamic datasets: Sources cited inline within `chemeng/cementdata.pyx` (NIST, Holland & Powell, Mullite data, etc.).

License
-------
See `LICENSE`.

Installation (Python 2.7)
-------------------------
The project is currently pinned to Python 2.7 semantics (Cython `language_level=2`) and bundles a legacy pyOpt (vendored under `src/pyOpt-1.2.0/pyOpt`). A minimal, reproducible install:

1. Ensure system prerequisites:
	* Python 2.7 (including headers: `python-dev` or `python2-devel` package)
	* C/C++ compiler (e.g. `gcc`, `g++`)
	* (Optional but recommended) Fortran compiler (`gfortran`) for additional pyOpt optimizers
	* Make / build essentials (`build-essential` on Debian/Ubuntu)
2. (Recommended) Create and activate a virtual environment:
	```bash
	virtualenv -p python2.7 venv
	. venv/bin/activate
	```
3. Upgrade packaging tools compatible with Py2.7:
	```bash
	pip install --upgrade pip==20.3.4 setuptools wheel
	```
4. Install numeric deps first (choosing versions that still support Py2.7):
	```bash
	pip install numpy==1.16.6 Cython==0.29.36
	```
5. Build & install PyChemEng (will also install vendored pyOpt package):
	```bash
	python setup.py build
	python setup.py install
	```
6. Quick self‑test:
	```bash
	python -c "from chemeng import *; import chemeng.cementdata; print('Species count:', len(speciesData))"
	python Test.py
	```

Optional: Editable / development install:
```bash
python setup.py build_ext --inplace
export PYTHONPATH=$(pwd):$PYTHONPATH
```

Upgrading Numpy / Cython: Rebuild extensions after any upgrade:
```bash
pip uninstall chemeng -y
python setup.py clean --all
python setup.py build install
```

Troubleshooting Build Issues
----------------------------
Common problems and resolutions during compilation.

1. `ImportError: No module named Cython.Build`
	* Cython not installed. Install with: `pip install Cython==0.29.36`.

2. `fatal error: Python.h: No such file or directory`
	* Missing Python development headers. Install OS package (`sudo apt-get install python-dev` or distro equivalent).

3. `numpy/arrayobject.h: No such file or directory` or Numpy API mismatch warnings
	* Ensure numpy installed *before* building: `pip install numpy==1.16.6` then rebuild.

4. Fortran optimizer build warnings (pyOpt subpackages) / missing `.so` for certain optimizers
	* A Fortran compiler is absent. Install `gfortran`. pyOpt attempts to continue even if individual optimizers fail; core SLSQP should still work (if its build passes). Warnings look like `*** WARNING: Building of optimizer ... failed`.

5. `undefined reference` linker errors referencing Fortran symbols
	* Ensure `gfortran` present and that `LD_LIBRARY_PATH` includes its lib directory (rare on standard systems). Clean and rebuild.

6. Runtime import error after updating numpy or moving between machines
	* Binary extensions stale. Run: `python setup.py clean --all && python setup.py build install`.

7. Segmentation fault early in import
	* Usually due to ABI mismatch (compiled against different Python or numpy). Reinstall inside a fresh virtualenv as per steps above.

8. `ValueError: Buffer dtype mismatch` in Cython code
	* Numpy was upgraded beyond the compatible range. Pin to 1.16.x for Python 2.7.

9. pyOpt not found despite bundling
	* Ensure `pyOpt` appears in `site-packages` or your current directory is on `PYTHONPATH`. If performing an in‑place dev build, export `PYTHONPATH=$(pwd):$PYTHONPATH`.

10. `gcc: error: unrecognized command line option '-fstack-protector-strong'`
	* Older GCC toolchain. Update compiler or remove problematic flags (none are explicitly added here, but your distro may inject them; upgrade toolchain recommended).

Cleaning Everything
-------------------
```bash
python setup.py clean --all
find . -name "*.so" -delete
find . -name "*.c" -o -name "*.cpp" -o -name "*.pyc" -delete
```

Known Limitations (Current Py2.7 State)
--------------------------------------
* Python 2.7 end‑of‑life; security patches absent.
* Newer pyOpt releases require Python 3; we vendored a legacy snapshot for continuity.
* Consider future migration to Python 3 (adjust Cython `language_level=3` and syntax modernization) for longevity.

If Problems Persist
-------------------
Open an issue including: Python version, OS, compiler versions (`gcc --version`, `gfortran --version`), full build log (run with `python setup.py build -v`).