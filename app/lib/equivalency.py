"""
Equivalency engine.

Given two country schedules and a child's age in months, computes:
  - which antigens the child has received (assumed: all doses from country A up to their age)
  - which antigens country B requires by that same age
  - per-antigen coverage status
  - missing doses split into primary (foundational) and boosters (maintenance)

Primary and booster deficits are tracked separately so that, e.g., a child whose
primary series was covered by country A correctly shows the booster as still missing
rather than accidentally marking a primary dose as missing.
"""


def compute_equivalency(schedule_a, schedule_b, child_age_months):
    """
    Returns a dict with:
      - antigen_coverage:    list of per-antigen coverage dicts
      - missing_primary:     primary doses in country B not yet satisfied — higher urgency
      - missing_boosters:    booster doses in country B not yet satisfied — lower urgency
      - covered_doses:       doses in country B already satisfied
      - overall_status:      "up-to-date" | "boosters-only" | "missing-primary"
    """
    # Step 1 — tally antigens received in country A (all doses, primary and booster)
    received = {}  # antigen_id -> total count
    for dose in schedule_a["doses"]:
        if dose["ageMonths"] <= child_age_months:
            for antigen in dose["antigens"]:
                received[antigen] = received.get(antigen, 0) + 1

    # Step 2 — tally primary and booster requirements separately for country B
    b_due_doses = [d for d in schedule_b["doses"] if d["ageMonths"] <= child_age_months]

    primary_required = {}   # antigen_id -> count of primary doses required
    booster_required = {}   # antigen_id -> count of booster doses required
    for dose in b_due_doses:
        target = booster_required if dose.get("doseType") == "booster" else primary_required
        for antigen in dose["antigens"]:
            target[antigen] = target.get(antigen, 0) + 1

    # Step 3 — compute separate deficits
    # Received doses satisfy primary requirements first; any surplus rolls into boosters.
    all_antigens = set(primary_required) | set(booster_required) | set(received)

    primary_deficit = {}
    booster_deficit = {}
    for antigen in all_antigens:
        pri_req = primary_required.get(antigen, 0)
        bst_req = booster_required.get(antigen, 0)
        rec = received.get(antigen, 0)

        pri_covered = min(rec, pri_req)
        surplus = rec - pri_covered          # what's left after satisfying primary
        bst_covered = min(surplus, bst_req)

        primary_deficit[antigen] = pri_req - pri_covered
        booster_deficit[antigen] = bst_req - bst_covered

    # Step 4 — per-antigen coverage summary
    antigen_coverage = []
    total_required = {}
    for antigen in all_antigens:
        total_required[antigen] = primary_required.get(antigen, 0) + booster_required.get(antigen, 0)

    for antigen_id in sorted(all_antigens):
        req = total_required.get(antigen_id, 0)
        rec = received.get(antigen_id, 0)
        p_def = primary_deficit.get(antigen_id, 0)
        b_def = booster_deficit.get(antigen_id, 0)

        if req == 0:
            status = "extra"
        elif p_def == 0 and b_def == 0:
            status = "covered"
        elif p_def > 0:
            status = "partial" if rec > 0 else "missing"
        else:
            status = "boosters-pending"   # primary covered, booster(s) still needed
        antigen_coverage.append({
            "antigenId": antigen_id,
            "received": rec,
            "required": req,
            "status": status,
        })

    # Step 5 — classify each due dose in B as covered / missing-primary / missing-booster
    # Use the separate deficits so primary and booster gaps don't bleed into each other.
    p_deficit = dict(primary_deficit)
    b_deficit = dict(booster_deficit)

    missing_primary = []
    missing_boosters = []
    covered_doses = []

    for dose in sorted(b_due_doses, key=lambda d: d["ageMonths"]):
        is_booster = dose.get("doseType") == "booster"
        deficit = b_deficit if is_booster else p_deficit

        needs_any = any(deficit.get(a, 0) > 0 for a in dose["antigens"])
        if needs_any:
            if is_booster:
                missing_boosters.append(dose)
            else:
                missing_primary.append(dose)
            for a in dose["antigens"]:
                if deficit.get(a, 0) > 0:
                    deficit[a] -= 1
        else:
            covered_doses.append(dose)

    # Step 6 — overall status
    if missing_primary:
        overall_status = "missing-primary"
    elif missing_boosters:
        overall_status = "boosters-only"
    else:
        overall_status = "up-to-date"

    return {
        "antigen_coverage": antigen_coverage,
        "missing_primary": missing_primary,
        "missing_boosters": missing_boosters,
        "covered_doses": covered_doses,
        "overall_status": overall_status,
        "child_age_months": child_age_months,
    }
