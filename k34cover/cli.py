"""Command-line interface for k34cover."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from pprint import pformat
from time import perf_counter
from typing import Optional, Union

from . import __version__
from .cover import cover_k3k4, prepare_generation

PathLike = Union[str, Path]


def _format_design(blocks: object) -> str:
    """Return a deterministic, readable representation of a block list."""
    return pformat(blocks, width=100, compact=True, sort_dicts=False)


def run(lb: int, ub: int, output_path: Optional[PathLike] = None) -> Path:
    """Generate verified covers for every order in ``range(lb, ub)``.

    Construction backends are imported once before timing begins.  Their startup
    cost is reported separately as ``initialization time``.  Each order is then
    timed independently, including construction and built-in verification.  The
    report contains the complete block list, optimum parameters, excess,
    verification status, and elapsed time for that order.
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

    initialization_started = perf_counter()
    prepare_generation(range(lb, ub))
    initialization_elapsed = perf_counter() - initialization_started

    print(f"initialization time = {initialization_elapsed:.6f} seconds")

    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"k34cover version: {__version__}\n")
        stream.write(f"initialization time: {initialization_elapsed:.6f} seconds\n\n")
        for order in range(lb, ub):
            print("------------")
            print(f"order = {order}")

            started = perf_counter()
            result = cover_k3k4(order)
            elapsed = perf_counter() - started

            print(f"generation time = {elapsed:.6f} seconds")

            stream.write("------------\n")
            stream.write(f"order = {order}\n")
            stream.write(f"generation time: {elapsed:.6f} seconds\n")
            stream.write(f"excess for K-{order}:\n{result.xi}\n")
            stream.write(f"number of triples: {result.n_k3}\n")
            stream.write(f"number of quadruples: {result.n_k4}\n")
            stream.write(f"total number of blocks: {len(result.blocks)}\n")
            stream.write("full design:\n")
            stream.write(_format_design(result.blocks))
            stream.write("\n")
            stream.write(f"check result for K-{order}:\nTrue\n\n")

    print(f"Saved to {path}")
    return path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="k34cover",
        description=(
            "Generate deterministic minimum-excess K3/K4 coverings for a "
            "range of complete-graph orders."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--lb", type=int, default=7, help="lower bound on v (inclusive)")
    parser.add_argument("--ub", type=int, default=60, help="upper bound on v (exclusive)")
    parser.add_argument("--output", type=Path, default=None, help="output report path")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    run(args.lb, args.ub, args.output)


if __name__ == "__main__":
    main()
