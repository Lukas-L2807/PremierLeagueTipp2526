import requests

def get_comp_season_id(base, headers, label="2025/26", comp_id=1):
    # comp_id=1 is Premier League
    r = requests.get(f"{base}/compseasons", params={"comps": comp_id}, headers=headers, timeout=30)
    r.raise_for_status()
    for cs in r.json().get("compSeasons", []):
        if cs.get("label") == label:
            return cs.get("id")
    raise ValueError(f"Could not find compSeason with label {label}")