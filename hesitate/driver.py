import time
import random

from contextlib import contextmanager

from . import conf

AVG_TIMINGS = {}


@contextmanager
def timed(modpath, lineno, col_offset):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()

        key = (modpath, lineno, col_offset)

        total_time = end - start

        prev_time = AVG_TIMINGS.setdefault(key, total_time)
        new_time = conf.CONVERGENCE_FACTOR * total_time \
            + (1.0 - conf.CONVERGENCE_FACTOR) * prev_time

        AVG_TIMINGS[key] = new_time


def should_assert(modpath, lineno, col_offset):
    key = (modpath, lineno, col_offset)
    duration = AVG_TIMINGS.get(key)

    if duration is None:
        return random.random() < conf.INITIAL_PROBABILITY
    else:
        prob = conf.TARGET_TIMING / duration

        return random.random() < prob
