# Order 17

Order `v = 17` is intentionally excluded from the runtime generator.

The minimum excess is 2, but the secondary optimum block count is being treated
as a separate finite problem. The arithmetic lower-bound profile corresponding
to 28 blocks is

```text
excess = 2
K3 blocks = 10
K4 blocks = 18
```

This profile is **not** installed as an optimum software target. The package
does not claim that a 28-block covering exists. A 17-point construction will be
added only after the finite optimum is settled and an explicit certificate has
been independently verified.

The general residue-5 construction cannot be specialised to 17 through the
usual `3^u 6^1` route because that would require a 4-GDD of type `3^4 6^1`.
No larger runtime construction uses order 17 as a recursive ingredient.

Current behaviour:

```python
from k34cover.cover import cover_k3k4

cover_k3k4(17)  # raises NotImplementedError
```

The command-line interface records the order as `NOT IMPLEMENTED` and continues
with the requested interval.
