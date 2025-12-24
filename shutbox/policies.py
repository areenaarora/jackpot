import json
import random
from typing import List, Optional

# ---------- helpers (no dependence on Game.legal_moves) ----------------


def _call_or_val(x):
    return x() if callable(x) else x


def _open_tiles_list(game) -> List[int]:
    """Return open tiles as ints."""
    tiles = game.tiles
    if isinstance(tiles, dict):
        return [t for t, is_open in tiles.items() if is_open]
    return [t for t in tiles if t is not None]


def _tiles_to_key(game) -> str:
    """Key like '123X56X89' used in the learned table."""
    tiles_max = getattr(game, "tiles_max", 9)
    tiles = game.tiles
    if isinstance(tiles, dict):
        return "".join(
            str(i) if tiles.get(i, False) else "X" for i in range(1, tiles_max + 1)
        )
    present = set(t for t in tiles if t is not None)
    return "".join(str(i) if i in present else "X" for i in range(1, tiles_max + 1))


def _compute_legal_moves(game, roll_val: int) -> List[List[int]]:
    """Allow 1- or 2-tile moves that sum to the roll."""
    opens = _open_tiles_list(game)
    moves = [[t] for t in opens if t == roll_val]
    n = len(opens)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = opens[i], opens[j]
            if a + b == roll_val:
                moves.append([a, b])
    return moves


def _remaining_sum_after(game, mv: Optional[List[int]]) -> int:
    if mv is None:
        mv = []
    if hasattr(game, "remaining_sum_after"):
        return game.remaining_sum_after(mv)
    return sum(_open_tiles_list(game)) - sum(mv)


# ---------- learned/table policy --------------------------------------


def table_policy_loader(path: str):
    with open(path) as f:
        table = json.load(f)

    def pick_move(game):
        roll_val = int(_call_or_val(getattr(game, "roll")))
        legal = _compute_legal_moves(game, roll_val)
        if not legal:
            return None

        key = _tiles_to_key(game) + "|" + str(roll_val)
        hit = table.get(key)
        if hit:
            want = list(map(int, hit.split("+")))  # "8+3" -> [8, 3]
            if want in legal:
                return want

        # fallback: greedy (minimize remaining sum)
        return min(legal, key=lambda mv: _remaining_sum_after(game, mv))

    return pick_move


# ---------- baseline policies -----------------------------------------


def random_move(game) -> Optional[List[int]]:
    roll_val = int(_call_or_val(getattr(game, "roll")))
    legal = _compute_legal_moves(game, roll_val)
    return random.choice(legal) if legal else None


def greedy_move(game) -> Optional[List[int]]:
    roll_val = int(_call_or_val(getattr(game, "roll")))
    legal = _compute_legal_moves(game, roll_val)
    if not legal:
        return None
    return min(legal, key=lambda mv: _remaining_sum_after(game, mv))


def human_move(game) -> Optional[List[int]]:
    roll_val = int(_call_or_val(getattr(game, "roll")))
    legal = _compute_legal_moves(game, roll_val)
    if not legal:
        return None
    multi = [mv for mv in legal if len(mv) >= 2]
    if multi:
        return min(multi, key=lambda mv: _remaining_sum_after(game, mv))
    return greedy_move(game)


__all__ = ["table_policy_loader", "random_move", "greedy_move", "human_move"]
