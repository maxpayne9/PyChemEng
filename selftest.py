#!/usr/bin/env python
"""
Lightweight automated self-test for PyChemEng (Python 2.7 compatible).

Runs a sequence of fast sanity checks:
 1. Import core modules & cement data.
 2. Confirm presence of key species & phases.
 3. Basic thermodynamic property evaluations (Cp, enthalpy, entropy) monotonic / ranges.
 4. Simple adiabatic methane/air combustion equilibrium (checks temperature bounds).
 5. Simple water flash (liquid + vapour) equilibrium test.

Exits with code 0 on success, >0 on first failure. Prints a JSON summary to stdout.
"""
from __future__ import with_statement
import sys, json, traceback

RESULT = { 'steps': [], 'ok': True }

def record(name, ok, details=""):
    RESULT['steps'].append({'name': name, 'ok': bool(ok), 'details': details})
    if not ok:
        RESULT['ok'] = False

def step(func):
    def wrapper():
        try:
            func()
        except Exception as e:
            tb = traceback.format_exc()
            record(func.__name__, False, str(e) + "\n" + tb)
            raise
    return wrapper

@step
def import_modules():
    global chemeng, speciesData, Components, IdealGasPhase, IncompressiblePhase, findEquilibrium
    import chemeng
    from chemeng.speciesdata import speciesData
    from chemeng.components import Components
    from chemeng.phase import IdealGasPhase, IncompressiblePhase
    from chemeng.entropymaximiser import findEquilibrium
    import chemeng.cementdata  # populate cement & mineral species
    # Expose to globals
    globals().update(locals())
    record('import_modules', True, 'Imported core modules; species count=%d' % len(speciesData))

@step
def check_core_species():
    required = ['H2O', 'CO2', 'CH4', 'O2', 'N2']
    missing = [r for r in required if r not in speciesData]
    if missing:
        raise RuntimeError('Missing species: %s' % missing)
    record('check_core_species', True, 'All core species present')

@step
def check_cement_species():
    # Pick a few clinker/mineral phases likely present after cementdata import
    clinker = ['Ca3SiO5', 'Ca2SiO4', 'Ca3Al2O6']
    present = [c for c in clinker if c in speciesData]
    if not present:
        raise RuntimeError('No clinker species found among %s' % clinker)
    record('check_cement_species', True, 'Found clinker species: %s' % present)

@step
def thermo_consistency():
    sp = 'H2O'
    phase = 'Gas'
    T1, T2 = 298.15, 800.0
    h1 = speciesData[sp].Hf0(T1, phase)
    h2 = speciesData[sp].Hf0(T2, phase)
    if h2 <= h1:
        raise RuntimeError('Enthalpy not increasing with T for %s %s' % (sp, phase))
    cp = speciesData[sp].Cp0(500.0, phase)
    if cp <= 0:
        raise RuntimeError('Non-positive Cp for %s %s' % (sp, phase))
    record('thermo_consistency', True, 'ΔH > 0 and Cp positive')

@step
def combustion_equilibrium():
    # Adiabatic CH4 combustion (simple) – expect temperature > 1000 K and < 4000 K
    air = Components({'O2':0.21,'N2':0.79})
    fuel = Components({'CH4':1.0})
    elem = fuel.elementalComposition()
    reqO2 = elem['C'] + elem['H']/4.0
    mix = fuel + air * (reqO2 / air['O2'])
    products = Components({'CO2':0,'H2O':0,'CO':0,'OH':0,'O':0,'H':0,'NO':0})
    phase = IdealGasPhase(mix + products, T=298.15, P=1e5)
    out = findEquilibrium([phase], constP=True, constH=True, elemental=True)[0]
    if not (1000.0 < out.T < 4000.0):
        raise RuntimeError('Adiabatic flame T outside expected range: %g K' % out.T)
    record('combustion_equilibrium', True, 'Flame T=%.2f K' % out.T)

@step
def flash_equilibrium():
    # Simple water flash (Liquid + empty vapor) at constP,constH should generate some vapor at high T
    liq = IncompressiblePhase({'H2O':1.0}, T=373.15, P=1e5, phaseID='Liquid', molarvolume=0.018/998.0)
    vap = IdealGasPhase({'H2O':0.0}, T=300.0, P=1e5)
    res = findEquilibrium([liq, vap], constP=True, constH=True)
    vap_out = res[1]
    if vap_out.components['H2O'] <= 0.0:
        raise RuntimeError('No vapour produced in flash test')
    record('flash_equilibrium', True, 'Vapour moles=%.4f' % vap_out.components['H2O'])

def main():
    # Run steps sequentially; stop on first failure to save time.
    steps = [import_modules, check_core_species, check_cement_species, thermo_consistency, combustion_equilibrium, flash_equilibrium]
    for s in steps:
        try:
            s()
        except Exception:
            break
    print(json.dumps(RESULT, indent=2, sort_keys=True))
    sys.exit(0 if RESULT['ok'] else 1)

if __name__ == '__main__':
    main()
