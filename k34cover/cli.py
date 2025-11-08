# k34cover/cli.py

import argparse
from datetime import datetime
from typing import Optional

from .cover import cover_k3k4
from .verify import k3k4cover_checker
# from .utils.assign_diagonal import assign_diagonal  # optional, see comments below


def run(lb: int, ub: int, output_path: Optional[str] = None) -> None:
    """
    Core driver: loops over orders, builds covers, runs checks, and writes a report.
    """
    if output_path is None:
        # create a timestamp like 2025-11-03_11-44-27
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = f"output_{timestamp}.txt"

    with open(output_path, "w") as f:
        for order in range(lb, ub):
            if order % 12 in [0, 1, 2, 3, 4, 11]:
                print("------------")
                print(f"order = {order}")
                f.write("------------\n")
                f.write(f"order = {order}\n")

                # Build the cover
                res = cover_k3k4(order)
                design_ = res.blocks
                xi = res.xi
                n_triples = res.n_k3
                n_quads = res.n_k4

                # If you want the sorted cover, you can use sort_lost_of_tuples here instead
                # from k34cover.verify import sort_lost_of_tuples
                # design = sort_lost_of_tuples(design_)
                # f.write(f"design for K-{order}:\n{design}\n")

                f.write(f"excess for K-{order}:\n{xi}\n")
                f.write(f"number of triples: {n_triples}\n")
                f.write(f"number of quadruples: {n_quads}\n")

                # Optional diagonal assignment:
                # f.write("Assigning diagonal:\n")
                # dict_diagonal = assign_diagonal(design, order)
                # f.write(f"{dict_diagonal}\n")

                # Verification
                f.write(f"check result for K-{order}:\n")
                f.write(str(k3k4cover_checker(order, design_)) + "\n\n")

    print(f"Saved to {output_path}")


def main() -> None:
    """
    CLI entry point. This is what `k34cover` (from pyproject.toml) should call.
    """
    parser = argparse.ArgumentParser(
        description="Generate and check K3/K4 covers of K_v."
    )
    parser.add_argument("--lb", type=int, default=7, help="Lower bound on v (inclusive)")
    parser.add_argument("--ub", type=int, default=60, help="Upper bound on v (exclusive)")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (optional)",
    )
    args = parser.parse_args()

    run(args.lb, args.ub, args.output)


if __name__ == "__main__":
    main()
