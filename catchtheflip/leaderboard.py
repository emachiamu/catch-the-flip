"""Hand a submission file to the live leaderboard of the track.

The leaderboard (`LEADERBOARD_URL`) is a notebook on Aqora. It does not take an upload: when
you sign in there and press Submit, it reads the file `STORE_KEY` from *your* Aqora store,
scores it against the hidden labels of the test split and shows the result. So a submission
takes two steps: save the file to your store (this module), then press Submit on the
leaderboard with the same account.

    from catchtheflip import leaderboard, scoring
    scoring.write_submission("tierB.csv", my_score, my_decision)
    account = await leaderboard.save_signed_in("tierB.csv")    # in a notebook: asks you to sign in
    leaderboard.save("tierB.csv")                              # in a script, after `aqora login`

The leaderboard shows the score of the last file you submitted, not the best of your files:
compare your detectors on the validation split, and submit the one you believe in.
Both functions need the package `aqora` (`pip install "aqora>=0.39"`; it is installed in the
Aqora workspace).
"""

from __future__ import annotations

import csv
import io
import math
import pathlib

STORE_KEY = "catch-the-flip/tierB.csv"  # where the leaderboard looks, in the store of whoever signs in
LEADERBOARD_URL = "https://aqora.io/Alice_Bob/catch-the-flip-leaderboard"
HEADER = ["segment_id", "score", "decision"]


def check(body: bytes) -> int:
    """Check the format of a submission file as the leaderboard does, and return its number of rows.

    Raises a ValueError that says what is wrong. The leaderboard also checks that the file
    has one row for each segment of the test split.
    """
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("the file is not UTF-8 text") from None
    rows = [row for row in csv.reader(io.StringIO(text)) if row]
    if not rows or [cell.strip() for cell in rows[0]] != HEADER:
        raise ValueError(f"the first line must be {','.join(HEADER)}")
    for i, row in enumerate(rows[1:]):
        if len(row) != 3:
            raise ValueError(f"row {i + 1}: expected three columns")
        try:
            segment_id, score = int(row[0]), float(row[1])
        except ValueError:
            raise ValueError(f"row {i + 1}: segment_id must be an integer and score a number") from None
        if segment_id != i:
            raise ValueError(f"row {i + 1}: segment_id is {segment_id}, expected {i} (rows in the order of segment_id)")
        if not math.isfinite(score):
            raise ValueError(f"row {i + 1}: the score is not a finite number")
        if row[2].strip() not in ("0", "1"):
            raise ValueError(f"row {i + 1}: decision must be 0 or 1")
    return len(rows) - 1


def _read(path) -> bytes:
    body = pathlib.Path(path).read_bytes()
    check(body)
    return body


async def save_signed_in(path) -> str:
    """Save the submission file at `path` to the Aqora store of the person at the keyboard.

    To be awaited in a notebook cell. In an Aqora workspace the cell shows a sign-in link, and
    the file goes to the store of the account that signs in, whoever owns the workspace; on a
    laptop it goes to the account of `aqora login`. Returns the username of that account: sign
    in on the leaderboard with the same one.
    """
    import aqora

    body = _read(path)
    viewer = await aqora.viewer_login(["read:storage", "write:storage"])
    username = (await viewer.send("query { viewer { username } }"))["viewer"]["username"]
    store = aqora.Store(viewer)
    await store.put_async(STORE_KEY, body, content_type="text/csv")
    if await store.get_async(STORE_KEY) != body:
        raise RuntimeError(f"reading {STORE_KEY} back did not return what was written: save again")
    return username


def save(path) -> None:
    """Save the submission file at `path` to the Aqora store of the account of `aqora login`.

    For scripts on a laptop. In an Aqora workspace this is the store of the owner of the
    workspace, which is yours only in your own copy: `save_signed_in` is the safe choice there.
    """
    import aqora

    body = _read(path)
    store = aqora.Store()
    store.put(STORE_KEY, body, content_type="text/csv")
    if store.get(STORE_KEY) != body:
        raise RuntimeError(f"reading {STORE_KEY} back did not return what was written: save again")
