from __future__ import annotations

import argparse
import sys

from hydra.app import diagnostics, main


def cli() -> int:
    parser = argparse.ArgumentParser(prog="hydra")
    parser.add_argument("--diagnostics", action="store_true", help="Mostra o ambiente do WebEngine")
    args = parser.parse_args()
    if args.diagnostics:
        print(diagnostics())
        return 0
    return main()


if __name__ == "__main__":
    sys.exit(cli())
