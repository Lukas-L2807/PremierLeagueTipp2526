# Numeric stats
def take(dt_id, row):
    el = row.select_one(f'[data-testid="{dt_id}"]')
    return el.get_text(strip=True) if el else None