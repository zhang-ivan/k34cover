#!/usr/bin/env python3
"""Build the self-contained k34cover release zip application.

Run this script from the repository root (or any Python environment able to
execute this file).  The resulting ``.pyz`` contains only the active k34cover
package: version 0.4.3 has no third-party runtime dependency.  The optional
legacy ``galois`` helper is intentionally not bundled because it is not used by
the active generator.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
import zipapp
from pathlib import Path



def build(output: Path) -> Path:
    root = Path(__file__).resolve().parents[1]
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="k34cover-zipapp-") as tmp:
        stage = Path(tmp)
        shutil.copytree(
            root / "k34cover",
            stage / "k34cover",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
        )
        shutil.copy2(root / "LICENSE", stage / "LICENSE.txt")
        (stage / "__main__.py").write_text(
            "from k34cover.cli import main\n\nif __name__ == '__main__':\n    main()\n",
            encoding="utf-8",
        )
        zipapp.create_archive(
            stage,
            target=output,
            interpreter="/usr/bin/env python3",
            compressed=True,
        )

    output.chmod(0o755)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/k34cover-0.4.3.pyz"),
        help="output .pyz path",
    )
    args = parser.parse_args()
    path = build(args.output)
    print(path)


if __name__ == "__main__":
    main()
