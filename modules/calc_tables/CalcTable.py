import json
import os

from datetime import date

from modules.get_data.getPremierLeagueTable import get_premier_league_table
from modules.calc_tables.GetPlayerTeams import get_player_teams
from modules.calc_tables.CalcPlayerTables import build_player_tables

def calc_table():
    # base directory
    current_path = os.path.abspath(__file__)
    while True:
        if os.path.basename(current_path) == "PremierLeagueTipp2526":
            base_path = current_path
            break
        parent = os.path.dirname(current_path)
        if parent == current_path:  # reached filesystem root
            raise FileNotFoundError(f"Project folder '{"STRIKE_idea"}' not found.")
        current_path = parent
    
    filepath = os.path.join(base_path, "players", "players.json")
    
    with open(filepath, "r", encoding="utf-8") as f:
        players = json.load(f)
    
    url = 'https://www.premierleague.com/tables'
    table = get_premier_league_table(url)
    
    player_teams = get_player_teams(players)

    player_tables, summary = build_player_tables(table, player_teams)

    # Convert summary DataFrame → list of dicts
    summary_records = summary.to_dict(orient="records")

    # Convert each player's DataFrame → list of dicts
    players_records = {player: df.to_dict(orient="records") for player, df in player_tables.items()}

    # Bundle into one JSON object
    output = {
        "summary": summary_records,
        "players": players_records
    }

    # create output filepath
    today_str = date.today().strftime("%Y-%m-%d")   # e.g. "2025-09-03"
    output_filepath = os.join(base_path, "data", f"{today_str}.json")

    # Write to json file
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)