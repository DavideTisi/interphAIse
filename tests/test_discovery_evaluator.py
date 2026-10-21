import pytest
from pymatgen.analysis.phase_diagram import PDEntry
from interphaise.discovery_evaluator import Objective, evaluate_candidate, penalty_bin, ranking_key


def evaluate(toy_entries, voltage=0, gap=3):
    entries = toy_entries([])
    return evaluate_candidate('toy-Li2S', entries[2], electrode_entry=entries[2],
                              electrolyte_entry=entries[2], entries=entries,
                              voltage=voltage, band_gap_eV=gap, energy_source='synthetic')


def test_self_oxidation_and_units(toy_entries):
    assert evaluate(toy_entries)['self_decomposition_penalty'] == pytest.approx(0)
    result = evaluate(toy_entries, voltage=4)
    # Li2S -> S + 2 Li(reservoir): -4.5 + 2*4 = 3.5 eV per S.
    assert result['self_decomposition_penalty'] == pytest.approx(3.5)
    assert result['contact_reaction_energies'] == pytest.approx([-3.5, -3.5])
    assert not result['acceptable']


@pytest.mark.parametrize('gap,status', [(None,'incomplete'), (float('nan'),'incomplete'), (0,'ok'), (1.99,'ok')])
def test_insulation_gate(toy_entries, gap, status):
    result = evaluate(toy_entries, gap=gap)
    assert result['status'] == status
    assert not result['insulating']
    assert ranking_key(result) == (0,0,0)


def test_fixed_bins_adhesion_and_ties():
    a = {'status':'ok', 'insulating':True, 'penalty_bin':penalty_bin(.021,.02), 'weakest_adhesion_J_m2':1}
    b = dict(a, penalty_bin=penalty_bin(.039,.02), weakest_adhesion_J_m2=2)
    assert ranking_key(a) == ranking_key(b)
    assert ranking_key(b,require_adhesion=True) > ranking_key(a,require_adhesion=True)
    assert penalty_bin(.04,.02) == 2
    assert ranking_key(dict(a,weakest_adhesion_J_m2=None),require_adhesion=True) == (0,0,0)


def test_contact_interior_reaction():
    # Both endpoints stable; interior oxide product releases 1 eV/non-Li atom.
    entries = [PDEntry('Li',0), PDEntry('O',0), PDEntry('S',0), PDEntry('SO',-2)]
    result = evaluate_candidate('s',entries[2],electrode_entry=entries[1],
                               electrolyte_entry=entries[2],entries=entries,
                               voltage=0,band_gap_eV=3,energy_source='synthetic')
    assert result['self_decomposition_penalty'] == 0
    assert result['penalty'] == pytest.approx(1)
    assert result['contacts'][0]['second_non_Li_fraction'] == pytest.approx(.5)


def test_missing_pinned_entry(toy_entries):
    entries = toy_entries([])
    with pytest.raises(ValueError,match='Pinned entry'):
        evaluate_candidate('absent',PDEntry('Li2S',-12),electrode_entry=entries[2],
                           electrolyte_entry=entries[2], entries=entries,voltage=4,
                           band_gap_eV=3,energy_source='synthetic')


def test_pure_li_rejected(toy_entries):
    entries = toy_entries([])
    with pytest.raises(ValueError,match='Pure Li'):
        evaluate_candidate('li',entries[0],electrode_entry=entries[2],
                           electrolyte_entry=entries[2], entries=entries,voltage=0,
                           band_gap_eV=3,energy_source='synthetic')


def test_invalid_objective():
    with pytest.raises(ValueError):
        Objective(bin_width_eV=0)


def test_pinned_metastable_polymorph_is_not_replaced(toy_entries):
    entries = toy_entries([])
    higher = PDEntry('Li2S', entries[2].energy + .3)
    entries.append(higher)
    result = evaluate_candidate('higher',higher,electrode_entry=entries[2],
                               electrolyte_entry=entries[2],entries=entries,
                               voltage=0,band_gap_eV=3,energy_source='synthetic')
    assert result['self_decomposition_penalty'] == pytest.approx(.3)
    assert result['penalty'] == pytest.approx(.3)


def test_formula_unit_scaling_does_not_change_penalty(toy_entries):
    entries = toy_entries([])
    doubled = PDEntry('Li4S2', 2*entries[2].energy)
    entries.append(doubled)
    result = evaluate_candidate('doubled',doubled,electrode_entry=entries[2],
                               electrolyte_entry=entries[2],entries=entries,
                               voltage=4,band_gap_eV=3,energy_source='synthetic')
    assert result['penalty'] == pytest.approx(3.5)


@pytest.mark.parametrize('voltage',[0,1,2,4])
def test_linear_program_agrees_with_qhull(toy_entries,voltage):
    entries=toy_entries([])
    args=dict(electrode_entry=entries[2],electrolyte_entry=entries[3],entries=entries,
              voltage=voltage,band_gap_eV=3,energy_source='synthetic')
    lp=evaluate_candidate('toy',entries[2],**args)
    hull=evaluate_candidate('toy',entries[2],backend='qhull',**args)
    assert lp['contact_reaction_energies']==pytest.approx(hull['contact_reaction_energies'])
    assert lp['self_decomposition_penalty']==pytest.approx(hull['self_decomposition_penalty'])


def test_linear_program_multielement_contact():
    # Two non-Li dimensions, a stable interior product, and a spectator element.
    entries=[PDEntry('Li',0),PDEntry('S',0),PDEntry('O',0),PDEntry('P',0),
             PDEntry('LiS',-1),PDEntry('LiO',-2),PDEntry('LiSO',-5),PDEntry('PS',-3)]
    args=dict(electrode_entry=entries[4],electrolyte_entry=entries[5],entries=entries,
              voltage=1,band_gap_eV=3,energy_source='synthetic')
    lp=evaluate_candidate('toy',entries[4],**args)
    hull=evaluate_candidate('toy',entries[4],backend='qhull',**args)
    assert lp['contact_reaction_energies']==pytest.approx(hull['contact_reaction_energies'])
    assert lp['penalty']==pytest.approx(hull['penalty'])


def test_equilibrated_contact_does_not_hide_coating_instability(toy_entries):
    entries=toy_entries([])
    result=evaluate_candidate('toy',entries[2],electrode_entry=entries[2],
        electrolyte_entry=entries[2],entries=entries,voltage=4,band_gap_eV=3,
        energy_source='synthetic',objective=Objective(version='v3-draft',contact_reference='equilibrated'))
    assert result['contact_reaction_energies']==pytest.approx([0,0])
    assert result['absolute_contact_reaction_energies']==pytest.approx([-3.5,-3.5])
    assert result['penalty']==pytest.approx(3.5)
    assert not result['acceptable']


def test_equilibrated_objective_excludes_unrelated_endpoint_floor():
    entries=[PDEntry('Li',0),PDEntry('O',0),PDEntry('S',0),PDEntry('LiS',-1),PDEntry('LiO',-4)]
    result=evaluate_candidate('oxide',entries[4],electrode_entry=entries[3],
        electrolyte_entry=entries[3],entries=entries,voltage=2,band_gap_eV=3,
        energy_source='synthetic',objective=Objective(version='v3-draft',contact_reference='equilibrated'))
    assert result['endpoint_decomposition_penalties']['electrolyte']==pytest.approx(1)
    assert result['absolute_contact_reaction_energies']==pytest.approx([-1,-1])
    assert result['penalty']==pytest.approx(0)
    assert result['acceptable'] # criterion passes; endpoints are still unstable
