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