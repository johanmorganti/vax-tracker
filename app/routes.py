from flask import Blueprint, render_template, abort, request
from .lib.data import load_schedule, list_countries
from .lib.equivalency import compute_equivalency

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/schedule/<country_code>")
def schedule(country_code):
    schedule = load_schedule(country_code)
    if schedule is None:
        abort(404)

    # Group doses by age for display
    ages = {}
    for dose in schedule["doses"]:
        key = (dose["ageMonths"], dose["ageLabel"])
        ages.setdefault(key, []).append(dose)
    age_groups = [{"ageMonths": k[0], "ageLabel": k[1], "doses": v}
                  for k, v in sorted(ages.items())]

    return render_template("schedule.html", schedule=schedule, age_groups=age_groups)


@bp.route("/compare", methods=["GET", "POST"])
def compare():
    countries = list_countries()
    result = None
    form = {"from": "", "to": "", "age": ""}

    if request.method == "POST":
        from_code = request.form.get("from_country", "").strip()
        to_code = request.form.get("to_country", "").strip()
        age_raw = request.form.get("child_age", "").strip()
        form = {"from": from_code, "to": to_code, "age": age_raw}

        if from_code and to_code and age_raw:
            try:
                child_age = int(age_raw)
            except ValueError:
                child_age = None

            if child_age is not None and from_code != to_code:
                schedule_a = load_schedule(from_code)
                schedule_b = load_schedule(to_code)
                if schedule_a and schedule_b:
                    result = compute_equivalency(schedule_a, schedule_b, child_age)
                    result["schedule_a"] = schedule_a
                    result["schedule_b"] = schedule_b

    return render_template("compare.html", result=result, form=form)
