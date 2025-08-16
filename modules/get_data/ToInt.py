def to_int(x):
    if x is None:
        return None
    x = x.strip()
    if x.startswith("0") and x.isdigit():
        # e.g., "01" -> 1
        try:
            return int(x, 10)
        except:
            return None
    try:
        return int(x)
    except:
        return None