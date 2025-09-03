# modules/get_data/parsePremierLeagueStandings.py
from bs4 import BeautifulSoup
import pandas as pd

from modules.get_data.ToInt import to_int
from modules.get_data.take import take

def get_premier_league_table(html: str) -> pd.DataFrame:
    """
    Parse the Premier League standings table from HTML that contains:
      <div class="standings__table-container"><table class="standings-table">...</table></div>

    Returns a DataFrame with columns:
    Pos, Team, Played, Won, Drawn, Lost, GF, GA, GD, Points, Next
    """
    soup = BeautifulSoup(html, "lxml")

    table = soup.select_one("div.standings__table-container table.standings-table")
    if not table:
        raise ValueError("Could not find standings table with selector "
                         "'div.standings__table-container table.standings-table'.")

    rows = []
    for row in table.select('tbody [data-testid="standingsRow"]'):
        # Position (there are two position spans for different breakpoints; pick the first meaningful one)
        pos_els = row.select('[data-testid="standingsRowPosition"]')
        if not pos_els:
            # Some builds keep position in a single element
            pos_text = row.select_one(".standings-row__position")
            pos = pos_text.get_text(strip=True) if pos_text else None
        else:
            pos = pos_els[0].get_text(strip=True)

        # Team name (prefer the long one if present)
        team = None
        team_long = row.select_one('[data-testid="standingsTeamName"]')
        if team_long:
            team = team_long.get_text(strip=True)
        else:
            team_short = row.select_one(".standings-row__team-name-short")
            team = team_short.get_text(strip=True) if team_short else None

        played = take("standingsRowStatPlayed", row)
        won    = take("standingsRowStatWon", row)
        drawn  = take("standingsRowStatDrawn", row)
        lost   = take("standingsRowStatLost", row)
        gf     = take("standingsRowStatGoalFor", row)
        ga     = take("standingsRowStatGoalAgainst", row)
        gd     = take("standingsRowStatGoalDifference", row)
        pts    = take("standingsRowPoints", row)

        # Next opponent (read the alt text from the badge in the 'next team' cell if available)
        next_cell = row.select_one('[data-testid="standingsRowNextTeam"]')
        next_team = None
        if next_cell:
            # Try alt text (e.g., "Newcastle United club badge")
            img = next_cell.select_one("img[alt]")
            if img and img.has_attr("alt"):
                alt = img["alt"].strip()
                next_team = alt.replace(" club badge", "")
            # If no image/alt, keep None

        rows.append({
            "Pos":    to_int(pos),
            "Team":   team,
            "Played": to_int(played),
            "Won":    to_int(won),
            "Drawn":  to_int(drawn),
            "Lost":   to_int(lost),
            "GF":     to_int(gf),
            "GA":     to_int(ga),
            "GD":     to_int(gd),
            "Points": to_int(pts),
            "Next":   next_team,
        })

    df = pd.DataFrame(rows).dropna(subset=["Pos", "Team"]).sort_values("Pos").reset_index(drop=True)
    return df