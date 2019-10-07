def string_distance(a: str, b: str):
    """
    Returns the levenshtein distance between two strings, which can be used to compare their similarity
    
    [Code source](https://github.com/TheAlgorithms/Python/blob/master/strings/levenshtein_distance.py)
    """
    if len(a) < len(b): return string_distance(b, a)
    if len(b) == 0: return len(a)
    prow = range(len(b) + 1)
    for i, c1 in enumerate(a):
        crow = [i + 1]
        for j, c2 in enumerate(b):
            ins = prow[j + 1] + 1
            dl = crow[j] + 1
            sub = prow[j] + (c1 != c2)
            crow.append(min(ins, dl, sub))
        prow = crow
    return prow[-1]