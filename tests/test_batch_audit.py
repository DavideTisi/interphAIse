import pytest
from scripts.audit_discovery_batch import paired_acceptance


def test_exact_paired_test_uses_discordant_pairs():
    a={i:True for i in range(10)};b={i:False for i in range(10)}
    r=paired_acceptance(a,b)
    assert r['left_only']==10 and r['right_only']==0
    assert r['exact_two_sided_mcnemar_p']==pytest.approx(2/1024)
    assert paired_acceptance(a,a)['exact_two_sided_mcnemar_p']==1.
    with pytest.raises(ValueError,match='identical seed'):
        paired_acceptance(a,{})
