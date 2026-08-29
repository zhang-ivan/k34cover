"""Compatibility import for the legacy projective-plane helper.

The active covering pipeline uses direct transversal designs and does not
import this module.  New code should import :mod:`k34cover.legacy.pg2`.
"""

from k34cover.legacy.pg2 import pg2

__all__ = ["pg2"]
