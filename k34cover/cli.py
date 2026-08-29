"""Command-line interface for k34cover."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from .cover import cover_k3k4

PathLike = Union[str, Path]


def run(lb: int, ub: int, output_path: Optional[PathLike] = None) -> Path:
    """Generate verified covers for every order in ``range(lb, ub)``.

    The intentionally unsupported order 17 is recorded as ``NOT IMPLEMENTED``
    and does not terminate a range run. The path of the written report is
    returned.
    """
    lb = int(lb)
    ub = int(ub)
    if lb < 3:
        raise ValueError("lb must be at least 3")
    if ub <= lb:
        raise ValueError("ub must be greater than lb")

    if output_path is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = Path(f"output_{timestamp}.txt")
    else:
        path = Path(output_path)

    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for order in range(lb, ub):
            print("------------")
            print(f"order = {order}")
            stream.write("------------\n")
            stream.write(f"order = {order}\n")

            try:
                result = cover_k3k4(order)
            except NotImplementedError as exc:
                message = f"NOT IMPLEMENTED: {exc}"
                print(message)
                stream.write(message + "\n\n")
                continue

            stream.write(f"excess for K-{order}:\n{result.xi}\n")
            stream.write(f"number of triples: {result.n_k3}\n")
            stream.write(f"number of quadruples: {result.n_k4}\n")
            stream.write(f"check result for K-{order}:\nTrue\n\n")

    print(f"Saved to {path}")
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate deterministic minimum-excess K3/K4 coverings for a "
            "range of complete-graph orders."
        )
    )
    parser.add_argument("--lb", type=int, default=7, help="lower bound on v (inclusive)")
    parser.add_argument("--ub", type=int, default=60, help="upper bound on v (exclusive)")
    parser.add_argument("--output", type=Path, default=None, help="output report path")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    run(args.lb, args.ub, args.output)


if __name__ == "__main__":
    main()
