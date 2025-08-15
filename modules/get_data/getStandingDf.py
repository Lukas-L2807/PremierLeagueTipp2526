import pandas as pd
import requests

def get_standings_df(base, headers, comp_season_id):
    # Standings for a given compSeason
    r = requests.get(
        f"{base}/standings",
        params={"compSeasons": comp_season_id, "altIds": "true"},
        headers=headers,
        timeout=30
    )
    r.raise_for_status()
    data = r.json()

    # The API returns multiple tables (overall/home/away). We take the overall.
    overall = None
    for table in data.get("tables", []):
        if table.get("type", {}).get("value") == "TOTAL":
            overall = table
            break
    if overall is None:
        raise RuntimeError("No overall standings found in API response.")

    rows = []
    for pos in overall.get("entries", []):
        team = pos["team"]
        stats = pos["stats"]  # list of dicts with 'name' and 'value'
        stat_map = {s["name"]: s["value"] for s in stats}
        rows.append({
            "Team": team.get("name"),
            "Played": stat_map.get("matchesPlayed"),
            "Won": stat_map.get("wins"),
            "Drawn": stat_map.get("draws"),
            "Lost": stat_map.get("losses"),
            "GF": stat_map.get("goalsFor"),
            "GA": stat_map.get("goalsAgainst"),
            "GD": stat_map.get("goalDifference"),
            "Points": stat_map.get("points")
        })

    df = pd.DataFrame(rows).sort_values("Pos").reset_index(drop=True)
    return df