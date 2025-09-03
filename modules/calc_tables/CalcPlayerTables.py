import pandas as pd
from typing import Dict, Tuple, List

def build_player_tables(
    table: pd.DataFrame,
    players: Dict[str, List[str]],
    team_col: str = "Team",
) -> Tuple[Dict[str, pd.DataFrame], pd.DataFrame]:
    """
    Parameters
    ----------
    table : DataFrame
        Master table containing all teams for all players.
        Must include a team identifier column (default: 'Team').
    players : dict
        {player_name: [team_name, ...]} from load_players().
    team_col : str
        Column in df that holds the team names to match against.

    Returns
    -------
    player_tables : dict[str, DataFrame]
        For each player, a DataFrame with only that player's teams and
        with the LAST COLUMN removed.
    summary : DataFrame
        Index: player names. Columns: sums of df columns 3..end (1-based).
    """
    if team_col not in table.columns:
        raise ValueError(f"Column '{team_col}' not found in df. Available: {list(table.columns)}")

    # drop last column
    if table.shape[1] >= 1:
        table = table.iloc[:, :-1] 
    
    # Per-player filter table to their teams
    player_tables: Dict[str, pd.DataFrame] = {}
    for player, team_names in players.items():
        pl = table[table[team_col].isin(team_names)].copy()
        player_tables[player] = pl

    # 2) Summary: sum each numeric column from 3rd onward
    if table.shape[1] >= 3:
        candidate_cols = list(table.columns[2:])
    else:
        candidate_cols = []
    numeric_cols = [c for c in candidate_cols if pd.api.types.is_numeric_dtype(table[c])]

    summary_rows = []
    for player, team_names in players.items():
        pl_full = table[table[team_col].isin(team_names)]
        sums = pl_full[numeric_cols].sum(numeric_only=True)
        sums["name"] = player
        summary_rows.append(sums)

    summary = pd.DataFrame(summary_rows).fillna(0)

    sort_cols = [c for c in ["Points", "GD", "GF"] if c in summary.columns]
    if not sort_cols:
        raise ValueError("None of ['Points', 'GD', 'GF'] found in summary columns.")
    summary = summary.sort_values(by=sort_cols, ascending=[False] * len(sort_cols)).reset_index(drop=True)

    summary.insert(0, "position", range(1, len(summary) + 1))
    summary.insert(1, "name", summary.pop("name"))

    return player_tables, summary