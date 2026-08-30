# Changelog

All notable changes to this project are recorded here.

The project follows semantic versioning while the public API remains in the
0.x development series.

## 0.4.3 - 2026-08-30

### Startup and timing

- Separated one-time construction-backend initialization from per-order
  generation timings.  The first requested order therefore no longer absorbs
  Python import cost.
- Reports now include a top-level initialization time followed by independent
  construction-and-verification times for each requested order.

### Runtime dependency reduction

- Removed SymPy and mpmath from the active runtime and standalone executable.
- Added compact exact deterministic helpers for primality, integer
  factorisation, and irreducible-polynomial testing over finite prime fields.
- Reduced the standalone `.pyz` from a dependency-bundled application to a
  package-only executable, substantially reducing archive size and cold-start
  overhead.

## 0.4.2 - 2026-08-30

### Reports and timing

- Command-line reports now contain the complete generated block list for every
  requested order.
- Added an independent high-resolution elapsed-time measurement for each order.
  The reported time covers construction and the built-in verification performed
  before the design is returned.
- Terminal progress output now reports the elapsed time for each generated
  order separately.

### Documentation and maintenance

- Normalised the presentation of all explicitly stored finite optimum seeds;
  none is documented as a separate special case.
- Updated the user manual, construction notes, verification record, release
  metadata, tests, and standalone-build workflow to match the report format.

## 0.4.1 - 2026-08-30

### Installation and distribution

- Added a self-contained executable Python zip application (`.pyz`) for normal
  command-line use without `pip`, a virtual environment, or administrator
  privileges.
- Rewrote installation instructions for PEP 668-managed Ubuntu/Debian Python
  installations.
- Made `pipx` the recommended persistent command-line installation method and
  documented project-local virtual environments for development.
- Added `docs/INSTALLATION.md` and a reproducible `scripts/build_zipapp.py`
  release builder.
- Added `python -m k34cover` support and a `--version` command-line option.

## 0.4.0 - 2026-08-30

### Complete spectrum

- Completed the set of fixed finite optimum coverings required by the runtime
  dispatcher.
- Updated the exact finite optimum-parameter table used by the verifier.
- The public generator now supports every integer order `v >= 3`.
- Updated the README, construction map, verification record, package metadata,
  citation metadata, Zenodo metadata, and regression tests for full-spectrum
  support.

## 0.3.1 - 2026-08-29

### Repository and documentation

- Reorganised project notes into a `docs/` directory.
- Rewrote the main README as the user and developer manual for the current
  three-family implementation.
- Added `CITATION.cff`, `CONTRIBUTING.md`, and GitHub Actions regression tests.
- Updated package metadata and Zenodo metadata for the current release.
- Removed the obsolete original-version README and internal transition notes
  from the repository root.

### Licensing

- Replaced the former CC BY-NC 4.0 notice with the custom **K34Cover
  Non-Commercial Limited Modification License v1.0**.
- The new license permits non-commercial use and redistribution of unmodified
  copies, permits private/internal non-commercial modifications, and requires
  prior written permission for commercial use or public redistribution of
  modified versions.

### Interface quality

- Improved command-line validation and UTF-8 report writing.
- Removed development-only `__main__` debug blocks and stale commented debug
  statements from active construction modules.

## 0.3.0 - 2026-08-29

### Construction architecture

- Unified residues `0,1,2,3,4,11 (mod 12)` under direct 0/1/2-point
  BIBD(4) truncation.
- Unified residues `5,7,8,10 (mod 12)` under one 7-hole PBD
  truncation/filling routine.
- Retained the Mills truncation as the distinct route for residues `6,9`.
- Reduced the top-level use of stored designs to a small fixed finite set.

### Performance and maintenance

- Added a fast successful path to cover verification.
- Removed redundant command-line re-verification.
- Added bounded caches for expensive reusable designs.
- Shared primitive PBD22/PBD46 ingredients and simplified finite seed dispatch.
- Isolated inactive historical helpers under `k34cover.legacy`.
