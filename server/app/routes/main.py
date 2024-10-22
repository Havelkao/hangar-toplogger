import pandas as pd
import statistics as st
from flask import render_template, Blueprint, Response
from app.data.jobs import get_view
from app.data.charts import Plot


main = Blueprint("main", __name__)

# look into caching
c = {}


@main.route("/", methods=["GET", "POST"])
def stats():
    figs = []

    if "grades" not in c:
        c["grades"] = get_view("vw_grade_agg")
        c["setters"] = get_view("vw_setter_agg")

    df = pd.DataFrame(c["grades"])
    df_s = pd.DataFrame(c["setters"])

    cards = [
        {"label": "Number of Routes", "value": sum(df["count"])},
        {
            "label": "Average Route Lifespan",
            "value": st.mean(df["lifespan_mean"]),
        },
        {
            "label": "Average Overgrade",
            "value": st.mean(df["accuracy"][lambda x: x > 0]),
        },
        {
            "label": "Average Undergrade",
            "value": st.mean(df["accuracy"][lambda x: x < 0]),
        },
    ]

    # GRADES
    count = Plot()
    count.ax.set_ylabel("# of Routes", **{"fontsize": 15, "fontweight": "bold"})
    c_bar = count.ax.bar(data=df, x="grade_label", height="count")
    count.bar_labels(df["count"], c_bar)
    count.remove_axis("y")

    acc = Plot()
    acc.ax.set_ylabel("Grade Accuracy", **{"fontsize": 15, "fontweight": "bold"})
    acc.ax.scatter(df["grade_label"], df["accuracy"])
    acc.ax.hlines(0, 0, len(df.index) - 1, linestyles="dashed", colors="black")

    median = Plot()
    median.ax.set_ylabel("Median of Ascends", **{"fontsize": 15, "fontweight": "bold"})
    median_bar = median.ax.bar(df["grade_label"], df["ascends_median"])
    median.bar_labels(df["ascends_median"], median_bar)
    median.remove_axis("y")

    daily = Plot()
    daily.ax.set_ylabel(
        "Average # of Daily Ascends", **{"fontsize": 15, "fontweight": "bold"}
    )
    daily_bar = daily.ax.bar(data=df, x="grade_label", height="ascends_daily_mean")
    daily.bar_labels(df["ascends_daily_mean"], daily_bar)
    daily.remove_axis("y")

    figs.extend(
        [
            count.encode,
            acc.encode,
            daily.encode,
            median.encode,
        ]
    )

    # SETTER
    setters = []
    acc_s = Plot(figsize=(10, 6))
    acc_s.ax.set_ylabel("Setter Accuracy", **{"fontsize": 15, "fontweight": "bold"})
    acc_s.ax.bar(df_s["setter_name"], df_s["accuracy"], width=0.4)
    acc_s.ax.tick_params(axis="x", labelrotation=90)
    acc_s.ax.hlines(0, 0, len(df_s.index) - 1, linestyles="dashed", colors="black")
    # acc_s.ax.bar(df_s["setter_name"], df_s["accuracy_abs"])

    count_s = Plot(figsize=(10, 6))
    count_s.ax.set_ylabel("# of Routes", **{"fontsize": 15, "fontweight": "bold"})
    c_bar_s = count_s.ax.bar(data=df_s, x="setter_name", height="count")
    count_s.bar_labels(df_s["count"], c_bar_s)
    count_s.ax.tick_params(axis="x", labelrotation=90)
    count_s.remove_axis("y")

    setters.extend([count_s.encode, acc_s.encode])

    return render_template("views/stats.html", figs=figs, setters=setters, cards=cards)


@main.route("/floor_plan", methods=["GET", "POST"])
def floor_plan():
    climbs = get_view("vw_climb_active")

    return render_template("views/floor_plan.html", climbs=climbs)


@main.route("/admin", methods=["GET", "POST"])
def admin():
    return render_template("views/admin.html")


@main.route("/admin/get", methods=["GET", "POST"])
def admin_get():
    return Response(status=200)
