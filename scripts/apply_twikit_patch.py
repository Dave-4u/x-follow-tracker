"""Apply twikit KEY_BYTE fix (X webpack format change). Run after pip install."""
from __future__ import annotations

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "patches" / "twikit_transaction.py"


def main() -> int:
    try:
        import twikit
    except ImportError:
        print("twikit not installed; pip install -r requirements.txt first", file=sys.stderr)
        return 1
    dest = pathlib.Path(twikit.__file__).resolve().parent / "x_client_transaction" / "transaction.py"
    if not SRC.is_file():
        print(f"missing patch file: {SRC}", file=sys.stderr)
        return 1
    shutil.copyfile(SRC, dest)
    print(f"Patched {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
