"""Apply twikit KEY_BYTE + User entities.urls fixes. Run after pip install."""
from __future__ import annotations

import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TRANSACTION_SRC = ROOT / "patches" / "twikit_transaction.py"
USER_SRC = ROOT / "patches" / "twikit_user.py"


def main() -> int:
    try:
        import twikit
    except ImportError:
        print("twikit not installed; pip install -r requirements.txt first", file=sys.stderr)
        return 1

    twikit_root = pathlib.Path(twikit.__file__).resolve().parent
    ok = True

    dest_tx = twikit_root / "x_client_transaction" / "transaction.py"
    if not TRANSACTION_SRC.is_file():
        print(f"missing patch file: {TRANSACTION_SRC}", file=sys.stderr)
        ok = False
    else:
        shutil.copyfile(TRANSACTION_SRC, dest_tx)
        print(f"Patched {dest_tx}")

    dest_user = twikit_root / "user.py"
    if not USER_SRC.is_file():
        print(f"missing patch file: {USER_SRC}", file=sys.stderr)
        ok = False
    else:
        shutil.copyfile(USER_SRC, dest_user)
        print(f"Patched {dest_user}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
