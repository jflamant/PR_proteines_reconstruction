#!/usr/bin/env python
from __future__ import division
from copy import deepcopy
from cPickle import loads, dumps

from periodictable import Ca,C,O,H,Fe,Ni,Si,D
from periodictable import formula, mix_by_weight, mix_by_volume

def test():
    ikaite=formula()
    # Note: this should be a tuple of tuples
    ikaite.structure = ((1,Ca),(1,C),(3,O), (6,((2,H),(1,O))))

    # Test print
    assert str(ikaite)=="CaCO3(H2O)6"

    # Test constructors
    assert ikaite==formula( [(1,Ca),(1,C),(3,O),(6,[(2,H),(1,O)])] )
    assert ikaite==formula( ikaite )
    assert ikaite is not formula(ikaite)
    assert ikaite.structure is formula(ikaite).structure

    # Test parsers
    assert formula("Ca") == formula([(1,Ca)])
    assert formula("Ca") == formula(Ca)
    assert formula("CaCO3") == formula([(1,Ca),(1,C),(3,O)])
    assert ikaite==formula("CaCO3+6H2O")
    assert ikaite==formula("(CaCO3+6H2O)1")
    assert ikaite==formula("CaCO3 6H2O")
    assert ikaite==formula("CaCO3(H2O)6")
    assert ikaite==formula("(CaCO3(H2O)6)1")
    assert ikaite.hill==formula("CCaO3(H2O)6").hill
    assert str(ikaite.hill) == "CH12CaO9"
    assert formula([(0.75,Fe),(0.25,Ni)])==formula("Fe0.75Ni0.25")

    # Test composition
    #print formula("CaCO3") + 6*formula("H2O")
    assert ikaite==formula( "CaCO3" ) + 6*formula( "H2O" )
    f = formula('')
    assert not (3*f).structure
    f = formula('H2O')
    assert id((1*f).structure) == id(f.structure)

    # Check atom count
    assert formula("Fe2O4+3H2O").atoms == {Fe:2,O:7,H:6}

    # Check the mass calculator
    assert formula('H2O').mass == 2*H.mass+O.mass
    assert formula("Fe2O4+3H2O").mass == 2*Fe.mass+7*O.mass+6*H.mass
    assert (formula("Fe2O[18]4+3H2O").mass
            == 2*Fe.mass+4*O[18].mass+3*O.mass+6*H.mass)

    assert (formula('D2O',natural_density=1).density
            == (2*D.mass + O.mass)/(2*H.mass + O.mass))

    # Test isotopes; make sure this is last since it changes ikaite!
    assert ikaite!=formula("CaCO[18]3+6H2O")
    assert formula("O[18]").mass == O[18].mass

    # Check x-ray and neutron sld
    rho,mu,inc = formula('Si',Si.density).neutron_sld(wavelength=4.5)
    rhoSi,muSi,incSi = Si.neutron.sld(wavelength=4.5)
    assert abs(rho - rhoSi) < 1e-14
    assert abs(mu - muSi) < 1e-14
    assert abs(inc - incSi) < 1e-14

    rho,mu = formula('Si',Si.density).xray_sld(wavelength=1.54)
    rhoSi,muSi = Si.xray.sld(wavelength=1.54)
    assert abs(rho - rhoSi) < 1e-14
    assert abs(mu - muSi) < 1e-14

    # Check that names work
    permalloy = formula('Ni8Fe2',8.692,name='permalloy')
    assert str(permalloy)=='permalloy'

    # Check that get/restore state works
    assert deepcopy(permalloy).__dict__ == permalloy.__dict__

    # Check that copy constructor works
    assert formula(permalloy).__dict__ == permalloy.__dict__
    assert formula('Si',name='Silicon').__dict__ != formula('Si').__dict__

    H2O = formula('H2O',natural_density=1)
    D2O = formula('D2O',natural_density=1)
    fm = mix_by_weight(H2O,3,D2O,2)
    fv = mix_by_volume(H2O,3,D2O,2)
    # quantity of H+D should stay in 2:1 ratio with O
    assert abs(fv.atoms[H]+fv.atoms[D] - 2*fv.atoms[O]) < 1e-14
    assert abs(fm.atoms[H]+fm.atoms[D] - 2*fm.atoms[O]) < 1e-14
    # H:D ratio should match H2O:D2O ratio when mixing by volume, but should
    # be skewed toward the lighter H when mixing by mass.
    assert abs(fv.atoms[H]/fv.atoms[D] - 1.5) < 1e-14
    assert abs(fm.atoms[H]/fm.atoms[D] - 1.5*D2O.density/H2O.density) < 1e-14
    # Mass densities should average according to H2O:D2O ratio when
    # mixing by volume but be skewed toward toward the more plentiful
    # H2O when mixing by mass
    H2O_fraction = 0.6
    assert abs(fv.density - (H2O.density*H2O_fraction + D2O.density*(1-H2O_fraction))) < 1e-14
    H2O_fraction = (3/H2O.density) / (3/H2O.density + 2/D2O.density)
    assert abs(fm.density - (H2O.density*H2O_fraction + D2O.density*(1-H2O_fraction))) < 1e-14

    # Make sure we are independent of unit cell size
    H2O = formula('3.2H2O',natural_density=1)
    D2O = formula('4.1D2O',natural_density=1)
    fm = mix_by_weight(H2O,3,D2O,2)
    fv = mix_by_volume(H2O,3,D2O,2)
    # quantity of H+D should stay in 2:1 ratio with O
    assert abs(fv.atoms[H]+fv.atoms[D] - 2*fv.atoms[O]) < 1e-14
    assert abs(fm.atoms[H]+fm.atoms[D] - 2*fm.atoms[O]) < 1e-14
    # H:D ratio should match H2O:D2O ratio when mixing by volume, but should
    # be skewed toward the lighter H when mixing by mass.
    assert abs(fv.atoms[H]/fv.atoms[D] - 1.5) < 1e-14
    assert abs(fm.atoms[H]/fm.atoms[D] - 1.5*D2O.density/H2O.density) < 1e-14
    # Mass densities should average according to H2O:D2O ratio when
    # mixing by volume but be skewed toward toward the more plentiful
    # H2O when mixing by mass
    H2O_fraction = 0.6
    assert abs(fv.density - (H2O.density*H2O_fraction + D2O.density*(1-H2O_fraction))) < 1e-14
    H2O_fraction = (3/H2O.density) / (3/H2O.density + 2/D2O.density)
    assert abs(fm.density - (H2O.density*H2O_fraction + D2O.density*(1-H2O_fraction))) < 1e-14

    # Pickle test
    assert loads(dumps(fm)) == fm
    ion = Fe[56].ion[2]
    assert id(loads(dumps(ion))) == id(ion)

    # zero quantities tests in mixtures
    f = mix_by_weight(H2O,0,D2O,2)
    assert f == D2O
    f = mix_by_weight(H2O,2,D2O,0)
    assert f == H2O
    f = mix_by_weight(H2O,0,D2O,0)
    assert f == formula()
    f = mix_by_volume(H2O,0,D2O,2)
    assert f == D2O
    f = mix_by_volume(H2O,2,D2O,0)
    assert f == H2O
    f = mix_by_volume(H2O,0,D2O,0)
    assert f == formula()

    # mix by weight with unknown component density
    # can't do mix by volume without component densities
    glass = mix_by_weight('SiO2',75,'Na2O',15,'CaO',10,density=2.52)

if __name__ == "__main__": test()
