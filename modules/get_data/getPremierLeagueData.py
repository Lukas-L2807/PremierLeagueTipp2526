from modules.get_data.getCompSeasonID import get_comp_season_id

def get_premier_league_data():
    base = "https://footballapi.pulselive.com/football"
    headers = {
        # These headers help mimic a normal browser request to the PL site
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.premierleague.com",
        "Referer": "https://www.premierleague.com/",
    }
    comp_season_id = get_comp_season_id(base, headers)
    table = get_premier_league_data(base, headers, comp_season_id)

    print(table)