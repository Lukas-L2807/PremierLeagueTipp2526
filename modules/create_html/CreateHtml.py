import json
import os
import sys

from datetime import datetime
from pathlib import Path
from html import escape

def infer_table(data):
    """
    Accepts either:
      - {"columns":[...], "rows":[{...}, {...}]}
      - [{"colA":..., "colB":...}, {...}]
    Returns (columns, rows_as_list_of_dicts)
    """
    if isinstance(data, dict) and "columns" in data and "rows" in data:
        columns = data["columns"]
        rows = data["rows"]
        # Ensure rows are dicts (convert list rows to dict if needed)
        if rows and isinstance(rows[0], list):
            rows = [dict(zip(columns, r)) for r in rows]
        return columns, rows
    elif isinstance(data, list) and data:
        if isinstance(data[0], dict):
            # union of keys, but preserve first row order
            first_cols = list(data[0].keys())
            rest_keys = []
            for r in data[1:]:
                for k in r.keys():
                    if k not in first_cols and k not in rest_keys:
                        rest_keys.append(k)
            columns = first_cols + rest_keys
            return columns, data
    # Fallback: empty table
    return [], []

def render_table(columns, rows):
    if not columns:
        return "<p><em>No data.</em></p>"
    # Build header
    thead = "<thead><tr>" + "".join(f"<th>{escape(str(c))}</th>" for c in columns) + "</tr></thead>"
    # Build body
    trs = []
    for r in rows:
        tds = "".join(f"<td>{escape(str(r.get(c, '')))}</td>" for c in columns)
        trs.append(f"<tr>{tds}</tr>")
    tbody = "<tbody>" + "".join(trs) + "</tbody>"
    return f"<table class='data-table'>{thead}{tbody}</table>"

def build_html(summary_section, players_section, title="Tables"):
    css = """
    :root {
      --bg:#0b1020; --card:#121834; --text:#e7eaf6; --muted:#aab0d6;
      --accent:#5b8cff; --border:#252b52; --table-stripe:#0f1530;
    }
    * { box-sizing:border-box; }
    html, body { margin:0; padding:0; font-family:Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:var(--bg); color:var(--text); }
    .wrap { max-width:1200px; margin:40px auto; padding:0 20px 60px; }
    h1 { font-size:28px; margin:0 0 20px; }
    h2 { font-size:22px; margin:30px 0 10px; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.25); }
    .data-table { width:100%; border-collapse:separate; border-spacing:0; font-size:14px; overflow:hidden; border-radius:12px; border:1px solid var(--border); }
    .data-table thead th { text-align:left; padding:10px 12px; background:linear-gradient(180deg, #1a2150, #141a3e); position:sticky; top:0; z-index:1; border-bottom:1px solid var(--border); }
    .data-table tbody td { padding:10px 12px; border-bottom:1px solid var(--border); }
    .data-table tbody tr:nth-child(odd) { background:var(--table-stripe); }
    .controls { display:flex; gap:8px; margin:12px 0 20px; flex-wrap:wrap; }
    .btn { background:transparent; color:var(--text); border:1px solid var(--border); padding:8px 12px; border-radius:10px; cursor:pointer; }
    .btn:hover { border-color:var(--accent); }
    .grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:16px; }
    @media (max-width:900px) { .grid { grid-template-columns:1fr; } }
    details.player { background:var(--card); border:1px solid var(--border); border-radius:16px; }
    details.player > summary { list-style:none; cursor:pointer; padding:14px 16px; font-weight:600; display:flex; align-items:center; gap:10px; }
    details.player > summary::-webkit-details-marker { display:none; }
    .chev { transition:transform .2s ease; display:inline-block; }
    details[open] .chev { transform:rotate(90deg); }
    .player-body { padding:0 16px 16px; }
    .muted { color:var(--muted); font-size:12px; }
    .hdr { display:flex; align-items:baseline; justify-content:space-between; gap:12px; margin-bottom:8px; }
    """
    js = """
    function expandAll() {
      document.querySelectorAll('details.player').forEach(d => d.open = true);
    }
    function collapseAll() {
      document.querySelectorAll('details.player').forEach(d => d.open = false);
    }
    """
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{escape(title)}</title>
<style>{css}</style>
<script>{js}</script>
</head>
<body>
  <div class="wrap">
    <div class="hdr">
      <h1>{escape(title)}</h1>
      <div class="muted" id="generated">Generated {escape(datetime.now().strftime('%Y-%m-%d %H:%M'))}</div>
    </div>

    <div class="card">
      <h2>Summary</h2>
      {summary_section}
    </div>

    <div class="controls">
      <button class="btn" onclick="expandAll()">Expand all players</button>
      <button class="btn" onclick="collapseAll()">Collapse all players</button>
    </div>

    <div class="grid">
      {players_section}
    </div>
  </div>
</body>
</html>"""

def render_player_block(name, table_html):
    safe_name = escape(str(name)) if name is not None else "Player"
    return f"""
    <details class="player">
      <summary><span class="chev">▶</span> {safe_name}</summary>
      <div class="player-body">
        {table_html}
      </div>
    </details>
    """

def order_columns(cols):
    preferred = ["Pos", "Position", "Team", "Played", "Won", "Drawn", "Lost", "GF", "GA", "GD", "Points"]
    seen = set()
    ordered = [c for c in preferred if c in cols and not seen.add(c)]
    # append any remaining columns in their original order
    ordered += [c for c in cols if c not in set(ordered)]
    return ordered

def make_html_from_json():
    # base directory
    current_path = os.path.abspath(__file__)
    while True:
        if os.path.basename(current_path) == "PremierLeagueTipp2526":
            base_path = current_path
            break
        parent = os.path.dirname(current_path)
        if parent == current_path:  # reached filesystem root
            raise FileNotFoundError(f"Project folder '{"PremierLeagueTipp2526"}' not found.")
        current_path = parent
    
    json_dir = os.path.join(base_path, "data")

    if not os.path.exists(json_dir):
        print(f"Folder {json_dir} does not exist")
        sys.exit(1)

    # Find all .json files and pick the most recently modified
    json_files = list(Path(json_dir).glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {json_dir}")
        sys.exit(1)

    latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
    print(f"Using latest JSON: {latest_json.name}")
    
    with open(latest_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expect top-level keys: "summary" and "players"
    # summary can be dict or list-of-rows; players is a list of {name, table} or {name, columns, rows}
    summary_cols, summary_rows = infer_table(data.get("summary", []))
    summary_html = render_table(summary_cols, summary_rows)

    players_html_blocks = []
    players = data.get("players", {})

    if isinstance(players, dict):
        # Your schema: { "Lukas": [ {...}, {...} ], "Mark": [ {...}, ... ] }
        for name, table_rows in players.items():
            p_cols, p_rows = infer_table(table_rows)  # table_rows is a list of dicts
            p_cols = order_columns(p_cols)
            players_html_blocks.append(
                render_player_block(name, render_table(p_cols, p_rows))
            )

    elif isinstance(players, list):
        # Fallback: old schemas where players is a list
        for p in players:
            if isinstance(p, dict):
                name = p.get("name", "Player")
                table_spec = p.get("table", p)
                p_cols, p_rows = infer_table(table_spec)
                p_cols = order_columns(p_cols)
                players_html_blocks.append(
                    render_player_block(name, render_table(p_cols, p_rows))
                )
            else:
                # just a string like "Lukas"
                players_html_blocks.append(
                    render_player_block(str(p), "<p><em>No table data.</em></p>")
                )

    html = build_html(summary_html, "\n".join(players_html_blocks), title="League Overview")

    out_file = os.path.join(base_path, f"table.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    return str(out_file)