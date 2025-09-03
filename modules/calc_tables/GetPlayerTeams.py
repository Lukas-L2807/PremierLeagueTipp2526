import json

def get_player_teams(players):
    result = {}
    for player in players:
        player_name = player["name"]
        team_names = [team["name"] for team in player["teams"]]
        result[player_name] = team_names

    return result