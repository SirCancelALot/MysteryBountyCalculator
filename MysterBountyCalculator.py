"""
Mystery Bounty Calculator
----------------------
Distributes a bounty pool among N players (1 envelope per player) using the
available amounts so that
  - Sum of all envelopes == Pool (exactly)
  - Number of envelopes == Number of players
  - Small amounts are frequent, large amounts are rare (power law)
"""

from itertools import permutations


def mystery_bounties(pool, players, amounts, min_one_each=False):
    """pool: Money Pool 
    players: Remaining player ammount
    amounts: List of bounty amounts
    min_one_each: does every ammount needs to be part at least once
    returns: dict {bounty amount: count}"""
    sortedAmmounts = sorted(set(amounts))
    ammountCount = len(sortedAmmounts)

    # --- 1. Feasibility ---------------------------------------------------
    if not (players * sortedAmmounts[0] <= pool <= players * sortedAmmounts[-1]):
        raise ValueError(
            f"Pool must be between {players * sortedAmmounts[0]} and {players * sortedAmmounts[-1]}."
        )
    floor = 1 if (min_one_each and players >= ammountCount and
                  sum(sortedAmmounts) + (players - ammountCount) * sortedAmmounts[0] <= pool) else 0

    # --- 2. Goal Distribution: Weight ~ amount^(-alpha) --------------------
    # Choose alpha using bisection so that the mean = pool/players
    mean = pool / players

    def weighted_mean(alpha):
        w = [x ** -alpha for x in sortedAmmounts]
        return sum(wi * xi for wi, xi in zip(w, sortedAmmounts)) / sum(w)

    lo, hi = -10.0, 10.0  # Mean decreases with alpha
    for _ in range(100):
        mid = (lo + hi) / 2
        if weighted_mean(mid) > mean:
            lo = mid
        else:
            hi = mid
    alpha = (lo + hi) / 2
    w = [x ** -alpha for x in sortedAmmounts]
    ideal = [players * wi / sum(w) for wi in w]

    # --- 3 rounds (Largest Remainder), note the minimum number ------------
    cnt = [max(floor, int(c)) for c in ideal]
    while sum(cnt) > players:  # too much -> subtract when the surplus is greatest
        i = max((i for i in range(ammountCount) if cnt[i] > floor),
                key=lambda i: cnt[i] - ideal[i])
        cnt[i] -= 1
    while sum(cnt) < players:  # too few -> add to the largest deficit
        i = max(range(ammountCount), key=lambda i: ideal[i] - cnt[i])
        cnt[i] += 1

    # --- 4. Trim the sum exactly to the pool ----------------------------------
    # An envelope changes from amount i to amount j; choose the move that
    # reduces the remaining difference the most and disrupts the distribution the least.
    def diff():
        return pool - sum(c * x for c, x in zip(cnt, sortedAmmounts))

    while diff() != 0:
        d = diff()
        best = None
        for i, j in permutations(range(ammountCount), 2):
            if cnt[i] <= floor:
                continue
            nd = d - (sortedAmmounts[j] - sortedAmmounts[i])
            if abs(nd) >= abs(d):
                continue
            dev = abs(cnt[i] - 1 - ideal[i]) + abs(cnt[j] + 1 - ideal[j]) \
                - abs(cnt[i] - ideal[i]) - abs(cnt[j] + 1 - 1 - ideal[j])
            key = (abs(nd), dev)
            if best is None or key < best[0]:
                best = (key, i, j)
        if best is None:
            raise ValueError("With these ammounts the pool is not exactly reachable (Check divididability/gcd).")
        _, i, j = best
        cnt[i] -= 1
        cnt[j] += 1

    return {x: c for x, c in zip(sortedAmmounts, cnt)}


if __name__ == "__main__":
        entries = 60
    #for entries in range(45, 91):
        pool = 20 * entries         
        players = 40
        amounts = [5, 10, 25, 50, 100, 250, 500, 1000]  

        result = mystery_bounties(pool, players, amounts)
        print(f"{'Bounty':>10} | {'Count':>6}")
        for b, c in result.items():
            print(f"{b:>9.2f}€ | {c:>6}")
        print("Pool:", sum(b * c for b, c in result.items()), "| Remaining Players:", sum(result.values()), "| Entries:", entries)