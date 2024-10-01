import requests
import json
import pandas as pd
import numpy as np


HANGAR_ID = 207
MY_ID = 1


def get_all_climbs(gym_id=HANGAR_ID):
    endpoint = f"https://api.toplogger.nu/v1/gyms/{gym_id}/climbs"
    r = requests.get(endpoint)
    return r.json()


def get_active_climbs(gym_id=HANGAR_ID):
    params = {"filters": {"deleted": False, "live": True}}
    endpoint = f"https://api.toplogger.nu/v1/gyms/{gym_id}/climbs.json?json_params={json.dumps(params)}"
    r = requests.get(endpoint)
    return r.json()


def get_user_ascends(uid=MY_ID, gym_id=HANGAR_ID):
    params = {
        "filters": {"used": True, "user": {"uid": uid}, "climb": {"gym_id": gym_id}}
    }
    params_url = json.dumps(params)
    endpoint = f"https://api.toplogger.nu/v1/ascends.json?json_params={params_url}&serialize_checks=true"
    r = requests.get(endpoint)
    return r.json()


def get_climb_stats(climb_id):
    endpoint = f"https://api.toplogger.nu/v1/gyms/207/climbs/{climb_id}/stats"
    r = requests.get(endpoint)
    return r.json()


def get_cgrade(climb_id):
    endpoint = f"https://api.toplogger.nu/v1/gyms/207/climbs/{climb_id}/stats"
    r = requests.get(endpoint)
    return r.json()["community_grades"]


def get_cgrades(series: pd.Series):
    try:
        r = requests.get("https://pastebin.com/raw/6JmsVuUR")
        data = r.json()
        return pd.DataFrame.from_dict(data)

    except:
        result = []
        for id in series:
            gcg = get_cgrade(id)
            if len(gcg) == 0:
                result.append([{"id": id}])
                continue
            for grade in gcg:
                grade["id"] = id
            result.append(gcg)

        f = pd.json_normalize(pd.DataFrame(result).stack()).dropna(how="all")
        f.to_json("cgrades.json")
        return f


def get_app_data():
    params_dict = {"includes": [{"gym": ["holds", "walls", "setters"]}, "setters"]}
    params = json.dumps(params_dict)
    endpoint = f"https://api.toplogger.nu/v1/users/248871.json?json_params={params}"
    headers = {
        "X-User-Email": "",
        "X-User-Token": "",
    }
    r = requests.get(endpoint, headers=headers)
    return r.json()


def cleanup_climbs(climbs, is_live=False):
    df = pd.DataFrame.from_dict(climbs)
    df.set_index("id", inplace=True)
    df["grade"] = df["grade"].astype(float)
    df["alt_grade"] = np.where(
        df["grade"].str[-2:].isin(["17", ".5"]),
        (df["grade"].astype(float) * 100 - 17) / 100,
        df["grade"],
    )
    df["alt_grade"] = np.where(
        df["grade"].str[-2:].isin(["83"]), df["grade"].astype(float) - 0.16, df["grade"]
    )
    df["alt_grade"] = df["alt_grade"].astype(float)
    df["date_live_start"] = pd.to_datetime(df["date_live_start"])
    df["date_live_end"] = pd.to_datetime(df["date_live_end"])
    df["lifespan"] = (df["date_live_end"] - df["date_live_start"]).dt.days
    df.rename(columns={"nr_of_ascends": "ascends"}, inplace=True)
    df["daily_ascends"] = df["ascends"] / df["lifespan"]
    df = df[
        [
            "alt_grade",
            "grade",
            "wall_id",
            "hold_id",
            "date_live_start",
            "date_live_end",
            "ascends",
            "average_opinion",
            "setter_id",
            "lifespan",
            "daily_ascends",
        ]
    ]

    # no route setter or wall id
    df.dropna(subset=["setter_id", "wall_id"], inplace=True)
    # exclude kids zone, rockets zone
    df = df[~df.wall_id.isin([2232, 2448])]

    if not is_live:
        # exclude active routes, and short-lived ones
        df = df[(df.lifespan >= 17)]
        # exclude weird easy route outliers with low ascends
        df = df[~df.index.isin([345454, 345451])]
        # exclude 0 ascends
        df = df[df.ascends >= 1]
        # exclude active routes, and short-lived ones
        df = df[(df.lifespan >= 17)]

    return df


def aggregate_analysis(df):
    absolute = df.groupby("grade").agg({"ascends": ["mean", "median", "std"]})
    relative = df.groupby("grade").agg({"daily_ascends": ["mean", "median" "std"]})

    return absolute.merge(relative, left_index=True, right_index=True)


grade_map = {
    "5.0": "5a",
    "5.17": "5a⁺",
    "5.33": "5b",
    "5.5": "5b⁺",
    "5.67": "5c",
    "5.83": "5c⁺",
    "6.0": "6a",
    "6.17": "6a⁺",
    "6.33": "6b",
    "6.5": "6b⁺",
    "6.67": "6c",
    "6.83": "6c⁺",
    "7.0": "7a",
    "7.17": "7a⁺",
    "7.33": "7b",
    "7.5": "7b+",
    "7.67": "7c",
    "7.83": "7c⁺",
    "8.0": "8a",
    "8.17": "8a⁺",
    "8.33": "8b",
    "8.5": "8b⁺",
    "8.67": "8c",
}


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def get_contrasting_color(hex_color):
    hex_color = hex_color.lstrip("#")
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    return (
        "#000000"
        if (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) > 150  # 186
        else "#ffffff"
    )
