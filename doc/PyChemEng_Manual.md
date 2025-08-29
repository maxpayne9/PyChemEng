# PyChemEng Manual

Comprehensive reference for the PyChemEng toolkit: concepts, APIs, thermodynamic models, equilibrium solver, and the cement / high‑temperature mineral data layer.

---
## 1. Architecture Overview

| Layer | Purpose | Key Objects |
|-------|---------|-------------|
| Elements (elementdata) | Atomic masses | elements dict |
| Species (speciesdata) | Standard-state thermo polynomials, phases | SpeciesDataType, PhaseData, ThermoConstantsType |
| Mixture Collections | Composition math | Components |
| Phases (phase.pyx) | State (T,P), mixture props, EOS assumptions | Phase, IdealGasPhase, IncompressiblePhase |
| Equilibrium (entropymaximiser) | Minimisation under constraints | EquilibriumFinder, findEquilibrium() |
| Domain Data (cementdata, NASADATA, etc.) | Populates species + coefficients | CementThermoData, CemThermoData, HPThermoData, MulliteThermoData |

---
## 2. Units & Conventions
* Temperature: Kelvin (K)
* Pressure: Pascal (Pa)
* Amounts: moles (mol)
* Energy: Joule (J)
* Cp & S (phase methods): J/K for the entire phase (extensive)
* Standard species functions (Cp0, Hf0, S0): molar basis (J/mol, J/mol/K)
* Molar masses: g/mol (`SpeciesDataType.mass`)
* Reference: T0 = 298.15 K, P0 = 1e5 Pa

---
## 3. Species Layer

### SpeciesDataType
Represents thermodynamic data for a species across one or more phase identifiers.

Attributes:
- `name`
- `mass` (g/mol): computed from elemental composition
- `elementalComposition` (Components of elements per mole species)
- `phases` : dict[str -> PhaseData]

Main methods:
- `Cp0(T, phase)` → J/mol/K
- `Hf0(T, phase)` → J/mol
- `S0(T, phase)` → J/mol/K
- `Gibbs0(T, phase)` → J/mol (Hf0 − T S0)
- `Pvap(T, phase)` (if Antoine data) → Pa
- `inDataRange(T, phase)` → bool
- `validRanges(phase)` → textual summary

### PhaseData
Holds lists of polynomial blocks (`constants`) and optional Antoine blocks (`antioneconstants`). Each block supplies Tmin, Tmax, and comments for provenance.

### Helper Functions
- `findSpeciesData(keyword="", composition=Components({}), elements=[])` → list[SpeciesDataType]
- `registerSpecies(name, elementalComposition)` – ensures all elements are known then adds species if new.

### Adding a New Species (Custom)
```python
from chemeng.speciesdata import registerSpecies, speciesData, ThermoConstantsType
from chemeng.components import Components

registerSpecies("XyZ", Components({'X':1,'Y':2,'Z':3}))
class MyPoly(ThermoConstantsType):
    def __init__(self):
        ThermoConstantsType.__init__(self, 300.0, 2000.0, "Example")
    def Cp0(self,T): return 30.0
    def Hf0(self,T): return -1.2e5 + 30.0*(T-298.15)
    def S0(self,T): return 200.0
speciesData['XyZ'].registerPhase('Gas')
speciesData['XyZ'].registerPhaseCoeffs(MyPoly(), 'Gas')
```

---
## 4. Components Class
A composition mapping species → moles with vector arithmetic.

Core methods:
- `total()` → total moles
- `totalMass()` → g
- `avgMolarMass()` → g/mol
- `elementalComposition()` → Components of elements (element→moles)
- `normalised()` → copy scaled to total()==1
- `keys()`, `values()`, `iteritems()`

Operators:
- `A + B` (new combined)
- `A - B`, unary `-` (negation)
- `A * k` (scale), `A / k`
- Indexing: `A['H2O']` -> moles (0 if absent); assignment allowed.

---
## 5. Phases
Represents a thermodynamic system of a mixture at (T,P) with a phase label used to select species data.

### Base `Phase`
Properties (extensive):
- `Cp()` J/K
- `enthalpy()` J
- `entropy()` J/K (ideal mixing + reference state)
- `gibbsFreeEnergy()` J
- `internalEnergy()` J
- `helmholtzFreeEnergy()` J
- `chemicalPotentials()` → Components (μ_i in J)
- `volume()` (abstract)

Helpers:
- `setEnthalpy(Htarget)` – solves for T
- `setInternalEnergy(Utarget)` – solves for T

### `IdealGasPhase`
- Adds pressure entropy term: −R n ln(P/P0)
- μ_i includes RT ln(P/P0)
- `volume() = n R T / P`
- `__add__` merges phases (enthalpy-conserving temperature resolution)

### `IncompressiblePhase`
- `enthalpy()` adds `(P−P0)V`
- Chemical potentials shift by `v (P − P0)`
- Requires `molarvolume` (m^3/mol estimated from density: V = M/ρ)

---
## 6. Thermodynamic Relationships
Implemented assumptions:
- Ideal mixing (activity ≈ mole fraction)
- Ideal gas where specified
- Pressure corrections only for ideal gas (entropy) & incompressible (Pv work term)
- Phase enthalpy/entropy are sums over species standard values + mixing entropy (for S)

If you need non‑ideal corrections (fugacity/activity coefficients), you would subclass `Phase` and override `entropy`, `chemicalPotentials`, etc.

---
## 7. Equilibrium Solver
`findEquilibrium(phases, *, constT=False, constP=False, constH=False, constV=False, constU=False, constS=False, elemental=False, Tmax=20000, Pmax=500, xtol=1e-5, logMolar=False, debug=False, Tmin=200.00001, iterations=50)`

Exactly two of (T,P,H,V,U,S) must be True.

Objective function selection:
- constT & constP → minimize Σ G / (R T)
- constT & constV → minimize Σ A / (R T)
- constH & constP → maximize S (implemented as minimize −S/R)
- constU & constV → maximize S (same form)
- constS & constV → minimize U
- constS & constP → minimize H

Constraints:
- Elemental species balances (`elemental=True`) OR fixed species totals (`elemental=False`).
- Selected extensive constraints appended (H/U/V/S).

Variables:
- Moles of each species in each phase (nonnegative; log domain if `logMolar=True`).
- T, P if not fixed (scaled by initial values).

Returns: List of Phase objects (copies) with equilibrium composition/state.

Usage pattern (adiabatic flame):
```python
phase = IdealGasPhase(fuel_air_mix + Components({'CO2':0,'H2O':0,'CO':0,'OH':0,'O':0,'H':0,'NO':0}), T=298.15, P=1e5)
result = findEquilibrium([phase], constP=True, constH=True, elemental=True)
flame = result[0]
print(flame.T)
```

Tips:
- Pass each physically distinct phase once (avoid duplicates – inflates mixing entropy).
- Provide product “slots” (zero-valued species) you expect may form; keep list tight to speed convergence.
- Use `logMolar=True` if huge disparities (trace radicals etc.).

---
## 8. Cement & High‑Temperature Mineral Data Layer
The module `chemeng.cementdata` populates a large suite of mineral / clinker / silicate / aluminate / ferrite species with several polynomial forms:

Polynomial classes:
- `CementThermoData` (7‑coefficient form: a[0..6] with powers T^-2, T^-1/2, constant, T, T^2, plus enthalpy & entropy integrals)
- `CemThermoData` (5‑coefficient simplified: Cp = a0 + a1 T + a2/T^2)
- `HPThermoData` (6‑coeff high‑T form including T^-1/2 term)
- `MulliteThermoData` (fixed coefficient array specialized for mullite)

Data sources (inline comments reference origins):
- NIST datasets
- Holland & Powell (2011) internally consistent metamorphic dataset
- Additional ACS / literature sources for specific borates, titanates, ferrites
- Mullite properties (Waldbaum, 1965)

Loading: `import chemeng.cementdata` automatically registers species and phases. Coefficients are pulled from CSV files located under `chemeng.config.datadir` (e.g., Cement.csv, NistData.csv, Cement_Therm_New2.csv).

Key clinker phases & typical labels (examples):
- `Ca3SiO5` (C3S) – phase="Crystal" or dataset specific phase names
- `Ca2SiO4` (C2S)
- `Ca3Al2O6` (C3A)
- `Ca4Al2Fe2O10` / related ferrites (if present in extended data)
- Spurrite, Tilleyite, Dolomite, Mullite, Sanidine, Albite, Diopside, Enstatite, Fayalite, etc.

Inspecting available phases:
```python
sp = speciesData['Ca3SiO5']
print sp.phases.keys()
print sp.phases['Crystal'].constants  # list of polynomial blocks
```

Temperature validity:
```python
speciesData['Ca3SiO5'].inDataRange(1600.0, 'Crystal')
```

Heat capacity, enthalpy of clinker phase at kiln temperature:
```python
T = 1773.15  # 1500 °C
cp = speciesData['Ca3SiO5'].Cp0(T, 'Crystal')  # J/mol/K
h  = speciesData['Ca3SiO5'].Hf0(T, 'Crystal')  # J/mol
```

### Cement Process Example: Raw Meal to Clinker Equilibrium (Simplified)
```python
import chemeng.cementdata
raw_meal = Components({'CaCO3':76.09,'SiO2':14.43,'Al2O3':3.90,'Fe2O3':2.27})  # wt% like basis -> convert to moles
# Convert weight % to moles (pseudo example):
meal_moles = Components({})
for sp,w in raw_meal.iteritems():
    meal_moles[sp] = w / speciesData[sp].mass  # w in grams, assuming 100 g basis

# Decompose carbonates manually or include gaseous species placeholders for equilibrium
feed = IdealGasPhase(Components({'CO2':0}) + meal_moles, T=1500+273.15, P=1e5)
# Add clinker product slots (if using elemental=True, you can start from oxides + CO2):
feed.components += Components({'Ca3SiO5':0,'Ca2SiO4':0,'Ca3Al2O6':0})
res = findEquilibrium([feed], constT=True, constP=True, elemental=True)[0]
print(res.components)
```
(For realistic clinker modeling you would include additional phases and possibly solids separately, not only an ideal gas phase; consider representing solids with `IncompressiblePhase` objects at the same T, P.)

---
## 9. Common Recipes

| Task | Snippet |
|------|---------|
| Molar mass of species | `speciesData['H2O'].mass` |
| Average mixture MW | `mix.avgMolarMass()` |
| Elemental composition of mixture | `mix.elementalComposition()` |
| Adiabatic combustion T | `findEquilibrium([phase], constP=True, constH=True, elemental=True)[0].T` |
| Saturation pressure (if defined) | `speciesData['H2O'].Pvap(T,'Liquid')` |
| Validate data range | `speciesData['Ca3SiO5'].validRanges('Crystal')` |
| Heat of vaporization | `(vap.enthalpy() - liq.enthalpy()) / nH2O` |

---
## 10. Error Handling & Diagnostics
- Unknown species key: index returns 0 moles in `Components`, but accessing thermodynamics via `speciesData[...]` raises KeyError.
- Out-of-range temperature: raises with message + validRanges.
- Equilibrium invalid constraints: raises if not exactly two constants selected.
- Optimizer failure: Exception with SLSQP status (try more iterations, simpler species set, adjust xtol).

Debug tips:
- `debug=True` in `findEquilibrium` will echo optimization problem definition.
- Reduce species list to isolate convergence issues.
- Use `logMolar=True` for trace species stability.

---
## 11. Performance Considerations
- Minimise number of zero-initialized product species.
- Avoid duplicate phases (each increases variables and entropy incorrectly).
- Reuse Components objects when constructing similar feeds (copy costs minor but cumulative).
- Consider pre-filtering species by required elements using `findSpeciesData` before building product slot lists.

---
## 12. Extending for Non‑Ideal Behavior
Subclass `Phase` and override:
- `entropy()` – to add activity coefficients (−R Σ n_i ln a_i)
- `chemicalPotentials()` – μ_i = μ_i^0 + RT ln a_i + excess terms
- `volume()` – implement EOS (e.g., cubic) for pressure effects

Then pass your custom phase instances into `findEquilibrium` (they must support the same interface as existing phases).

---
## 13. Provenance & Data Sources
See inline comments in `chemeng/cementdata.pyx` for references (NIST, Holland & Powell 2011, Mullite dataset, ACS sources). Always cite original thermodynamic compilations in publications.

---
## 14. Glossary
| Symbol | Meaning |
|--------|---------|
| Cp | Isobaric heat capacity (J/mol/K for species; J/K for phase) |
| Hf0(T) | Standard-state enthalpy (J/mol) |
| S0(T) | Standard-state entropy (J/mol/K) |
| G | Gibbs free energy (J) |
| A | Helmholtz free energy (J) |
| U | Internal energy (J) |
| V | Volume (m^3) |
| μ_i | Chemical potential of species i (J) |

---
## 15. License
See root `LICENSE` file.

---
## 16. Changelog (Manual)
* v1.0 (Generated): Initial comprehensive manual added; includes cement data layer section.

---
## 17. Future Enhancements (Ideas)
- Provide Python-level docstrings accessible via `help()`.
- Add per-mole helper methods (e.g., `phase.Cp_molar()`).
- Wrap equilibrium results in a lightweight object with metadata (iterations, tolerance achieved).
- Integrate non-ideal models (activity/fugacity) via plugin architecture.
- Convert CSV ingestion to a structured loader with validation & caching.

---
Generated automatically; adapt as project evolves.
