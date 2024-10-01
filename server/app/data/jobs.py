from .supabase import supabase
import pandas as pd
import requests


def get_view(name):
    response = supabase.table(name).select("*").execute()
    return response.data


def get_cgrade(climb_id):
    endpoint = f"https://api.toplogger.nu/v1/gyms/207/climbs/{climb_id}/stats"
    r = requests.get(endpoint)
    return r.json()["community_grades"]


def get_cgrades(series: pd.Series):
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
