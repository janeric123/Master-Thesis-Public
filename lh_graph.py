from itertools import combinations

# ---------------------------------------------------------------------------
# LH-Pfad Algorithmus
# ---------------------------------------------------------------------------

def advance(curr, drop, region_list, exclude_drop):
    """Ein einzelner Schritt des LH-Algorithmus für eine Seite (A oder B).

    curr:          aktuelle 3-elementige Region dieser Seite
    drop:          Label, das durch den letzten Zug der Gegenseite entfernt
                   werden muss
    region_list:   Kandidatenliste (A oder B), aus der die naechste Region
                   gesucht wird
    exclude_drop:  falls True, werden Regionen ausgeschlossen, die "drop"
                   wieder enthalten (verhindert das sofortige Zurueckgehen
                   zur vorherigen Region)

    Gibt (neue_region, neues_drop) zurück, oder (None, None) falls keine
    passende Region existiert - das bedeutet, der übergebene Graph ist
    nicht als LH-Graph realisierbar (kein gültiger Nachfolgeknoten).
    """
    reduced = curr - drop
    if exclude_drop:
        candidates = [r for r in region_list if reduced.issubset(r) and not drop.issubset(r)]
    else:
        candidates = [r for r in region_list if reduced.issubset(r)]

    if not candidates:
        return None, None

    new_region = candidates[0]
    new_drop = new_region - reduced
    return new_region, new_drop


def lh_graph_algorithm(A, B, r):
    """Führt den LH-Pfad-Algorithmus fuer Startlabel r aus.

    Gibt den Pfad als Liste von (curr_A, curr_B)-Paaren zurück, oder None,
    falls der Graph (A, B) nicht realisierbar ist, d.h. der Algorithmus an
    einer Stelle keinen gültigen Nachfolgeknoten findet.
    """
    curr_A = {1, 2, 3}
    curr_B = {4, 5, 6}

    if 1 <= r <= 3:
        curr_A, drop = advance(curr_A, {r}, A, exclude_drop=False)
        if curr_A is None:
            return None

        curr_B, drop = advance(curr_B, drop, B, exclude_drop=False)
        if curr_B is None:
            return None

        path = [(curr_A, curr_B)]

    elif 4 <= r <= 6:
        curr_B, drop = advance(curr_B, {r}, B, exclude_drop=False)
        if curr_B is None:
            return None

        curr_A, drop = advance(curr_A, drop, A, exclude_drop=False)
        if curr_A is None:
            return None

        path = [(curr_A, curr_B)]

        if curr_A | curr_B == {1, 2, 3, 4, 5, 6}:
            return path

        curr_B, drop = advance(curr_B, drop, B, exclude_drop=True)
        if curr_B is None:
            return None

        path.append((curr_A, curr_B))

    else:
        raise ValueError("r muss zwischen 1 und 6 liegen")

    while True:
        if curr_A | curr_B == {1, 2, 3, 4, 5, 6}:
            return path

        curr_A, drop = advance(curr_A, drop, A, exclude_drop=True)
        if curr_A is None:
            return None
        path.append((curr_A, curr_B))

        if curr_A | curr_B == {1, 2, 3, 4, 5, 6}:
            return path

        curr_B, drop = advance(curr_B, drop, B, exclude_drop=True)
        if curr_B is None:
            return None
        path.append((curr_A, curr_B))


# ---------------------------------------------------------------------------
# Enumeration der abstrakten Strategiesimplexe
# ---------------------------------------------------------------------------

def all_games():
    out = []
    V1 = [{1, 2, 4}, {1, 2, 5}, {1, 2, 6}]
    V2 = [{3, 2, 4}, {3, 2, 5}, {3, 2, 6}]
    V3 = [{1, 3, 4}, {1, 3, 5}, {1, 3, 6}]

    interior = [{4, 5, 6}, {1, 4, 5}, {1, 5, 6}, {1, 4, 6}, {2, 4, 5},
                {2, 5, 6}, {2, 4, 6}, {3, 4, 5}, {3, 5, 6}, {3, 4, 6}]
    for s1 in V1:
        for s2 in V2:
            for s3 in V3:
                #if s1 & s2 & s3 == set():
                for s4 in combinations(interior, r=4):
                    curr = [s1, s2, s3] + list(s4)
                    out.append(curr)

    return out


def filter_games(games):
    """Notwendige Bedingung: Gradsequenz [2,2,2,3,3,3,3]."""
    out = []
    for game in games:
        neighboor_count = []
        for vertex in game:
            neighboor_count.append(
            len([n for n in game if len(vertex - n) == 1]))
        if neighboor_count == [2, 2, 2, 3, 3, 3, 3]:
            out.append(game)

    return out


def change_player(game):
    out = []
    for vertex in game:
        out.append({(a + 2) % 6 + 1 for a in vertex})
    return out


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def run_games(games):
    out = []
    for s1 in games:
        for s2 in games:
            p2 = change_player(s2)
            for i in [1, 2, 3, 4, 5, 6]:
                path = lh_graph_algorithm(s1, p2, i)
                if path is None:
                    # (s1, p2) ist als LH-Graph nicht realisierbar für
                    # dieses Startlabel - ueberspringen statt abzustuerzen.
                    continue
                if len(path) >= 10:
                    out.append((s1, s2, i, path))
    return out


if __name__ == "__main__":
    games = all_games()
    print(f"Alle Strategiesimplexe: {len(games)}")

    filtered_games = filter_games(games)
    print(f"Nach Gradsequenz-Filter: {len(filtered_games)}")

    results = run_games(filtered_games)
    print(f"Gefundene Spiele mit Pfadlaenge >= 10: {len(results)}")
    for s1, s2, i, path in results:
        print(s1)
        print(s2)
        print(i)
        print(path)

    A = [{1,2,6}, {2,3,6}, {1,3,4}, {3,4,6}, {1,4,6}]
    B = [{5,6,3}, {4,5,3}, {4,6,2}, {4,1,2}, {4,1,3}, {6,2,3}, {1,2,3}]
    path = lh_graph_algorithm(A, B, 5)
    print(len(path))
    print(path)