# Driver must be included first to avoid recursive imports.

from . import driver

from .conf import set_initial_probability, \
    set_target_timing, set_convergence_factor
from .rewriter import attach_hook

__version__ = '0.0.2'

assert driver  # Dummy assertion to silence linting

__all__ = [
    'set_initial_probability', 'set_target_timing',
    'set_convergence_factor',

    'attach_hook',
]
