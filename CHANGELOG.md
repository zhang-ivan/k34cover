# Changelog

All notable changes to this project are recorded here.

The project follows semantic versioning while the public API remains in the
0.x development series.

## 0.4.0 - 2026-08-30

### Complete spectrum

- Added the verified optimum order-17 certificate with 12 triangles, 17
  quadruples, 29 total blocks, and excess edges `(1,2)` and `(1,3)`.
- Set `optimal_parameters(17)` to the exact optimum profile `(2, 12, 17)`.
- Added order 17 to the finite-exception dispatcher, closing the final gap.
- The public generator now supports every integer order `v >= 3`.

### Documentation and testing

- Rewrote the order-17 note from an open-case notice into the final certificate
  and optimum-parameter record.
- Updated the README, construction map, verification record, package metadata,
  citation metadata, and Zenodo metadata to describe full-spectrum support.
- Updated regression tests so consecutive sweeps and command-line tests include
  order 17.

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

- Clarified that order 17 is unresolved rather than merely missing a known
  optimum seed.
- `optimal_parameters(17)` now raises `NotImplementedError` instead of exposing
  an unproved 28-block profile as an optimum target.
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
- Reduced the top-level finite exception set to `6,8,9,10,18,19`.
- Kept order 17 explicitly unsupported and independent of all recursive routes.

### Performance and maintenance

- Added a fast successful path to cover verification.
- Removed redundant command-line re-verification.
- Added bounded caches for expensive reusable designs.
- Shared primitive PBD22/PBD46 ingredients and simplified finite seed dispatch.
- Isolated inactive historical helpers under `k34cover.legacy`.
