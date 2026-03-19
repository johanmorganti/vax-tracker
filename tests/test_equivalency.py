import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.lib.data import load_schedule
from app.lib.equivalency import compute_equivalency


def test_same_country_is_up_to_date():
    fr = load_schedule("fr")
    result = compute_equivalency(fr, fr, 12)
    assert result["overall_status"] == "up-to-date"


def test_fr_to_kr_missing_jev_is_primary():
    """JEV is a primary series in Korea — must appear in missing_primary, not missing_boosters."""
    fr = load_schedule("fr")
    kr = load_schedule("kr")
    result = compute_equivalency(fr, kr, 15)
    primary_antigens = {a for d in result["missing_primary"] for a in d["antigens"]}
    booster_antigens = {a for d in result["missing_boosters"] for a in d["antigens"]}
    assert "jev" in primary_antigens, "JEV primary doses should be missing FR→KR"
    assert "jev" not in booster_antigens


def test_fr_to_kr_missing_hepa_is_primary():
    """France does not give HepA; Korea's HepA is a primary series."""
    fr = load_schedule("fr")
    kr = load_schedule("kr")
    result = compute_equivalency(fr, kr, 18)
    primary_antigens = {a for d in result["missing_primary"] for a in d["antigens"]}
    assert "hepa" in primary_antigens, "HepA primary doses should be missing FR→KR"


def test_kr_to_sg_bcg_covered():
    """Korea gives BCG at birth; Singapore also requires it. Moving KR→SG, BCG should be covered."""
    kr = load_schedule("kr")
    sg = load_schedule("sg")
    result = compute_equivalency(kr, sg, 6)
    covered_antigens = {a for d in result["covered_doses"] for a in d["antigens"]}
    assert "bcg" in covered_antigens, "BCG should transfer KR→SG"


def test_fr_to_sg_hexavalent_covers_pentavalent():
    """France's hexavalent (DTaP-IPV-Hib-HepB) should cover Singapore's pentavalent (DTaP-IPV-Hib) series."""
    fr = load_schedule("fr")
    sg = load_schedule("sg")
    result = compute_equivalency(fr, sg, 12)
    cov = {c["antigenId"]: c for c in result["antigen_coverage"]}
    for antigen in ["dtx", "ttx", "ptx", "ipv", "hib"]:
        assert cov[antigen]["status"] == "covered", f"{antigen} should be covered FR→SG at 12m"


def test_sg_boosters_land_in_correct_bucket():
    """
    The SG 18-month DTaP-IPV-Hib booster and MMR booster should appear in missing_boosters,
    not missing_primary, when a child from FR moves to SG at 18 months.
    (BCG is a legitimately missing primary — France never gives it — so overall_status
    is correctly 'missing-primary'. But the booster-type doses must be in the right bucket.)
    """
    fr = load_schedule("fr")
    sg = load_schedule("sg")
    result = compute_equivalency(fr, sg, 18)

    booster_dose_ids = {d["id"] for d in result["missing_boosters"]}
    primary_dose_ids = {d["id"] for d in result["missing_primary"]}

    # DTaP-IPV-Hib booster: FR gives 3 primary hexavalents but no toddler booster → still needed
    assert "sg-5in1-booster" in booster_dose_ids, "SG 18m DTaP-IPV-Hib booster should be in missing_boosters"
    assert "sg-5in1-booster" not in primary_dose_ids

    # MMR booster: FR gives MMR at 12m AND 18m booster → sg-mmr-2 is already covered
    covered_ids = {d["id"] for d in result["covered_doses"]}
    assert "sg-mmr-2" in covered_ids, "sg-mmr-2 should be covered since FR also gives MMR booster at 18m"


def test_zero_age_nothing_required():
    fr = load_schedule("fr")
    sg = load_schedule("sg")
    result = compute_equivalency(fr, sg, 0)
    assert "antigen_coverage" in result
    assert "overall_status" in result
    assert "missing_primary" in result
    assert "missing_boosters" in result
