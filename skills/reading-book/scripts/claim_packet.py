#!/usr/bin/env python3
"""Place an exclusive claim on a review packet before starting a check, so it runs only once.

  python3 claim_packet.py <packet_dir> <owner>          # exit 0: claimed now; exit 3: already claimed
  python3 claim_packet.py <packet_dir> --show           # print the claim, if any

The claim is the file CLAIMED in the packet directory, created atomically (O_EXCL), holding the owner and time.
"""
from __future__ import annotations

import datetime as dt
import os
import pathlib
import sys


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    packet = pathlib.Path(argv[0])
    if not packet.is_dir():
        print(f"no packet directory: {packet}", file=sys.stderr)
        return 2
    claim = packet / "CLAIMED"
    if argv[1] == "--show":
        print(claim.read_text().strip() if claim.exists() else "unclaimed")
        return 0
    try:
        fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError:
        print(f"already claimed: {claim.read_text().strip()}")
        return 3
    with os.fdopen(fd, "w") as f:
        f.write(f"{argv[1]} {dt.datetime.now().isoformat(timespec='seconds')}\n")
    print(f"claimed by {argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
