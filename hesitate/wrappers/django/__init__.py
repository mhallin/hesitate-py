import hesitate

from django.conf import settings

_enable_hesitate = not settings.DEBUG

if hasattr(settings, 'HESITATE_ENABLED'):
    _enable_hesitate = settings.HESITATE_ENABLED

if _enable_hesitate:
    hesitate.attach_hook(
        initial_probability=getattr(settings, 'HESITATE_INITIAL_PROBABILITY', None),
        target_timing=getattr(settings, 'HESITATE_TARGET_TIMING', None),
        convergence_factor=getattr(settings, 'HESITATE_CONVERGENCE_FACTOR', None)
    )
