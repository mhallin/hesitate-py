import time
import random

from contextlib import contextmanager

INITIAL_PROBABILITY = 1.0
TARGET_TIMING = 0.1
AVG_TIMINGS = {}


def set_initial_probability(probability):
    assert 0 <= probability <= 1

    global INITIAL_PROBABILITY
    INITIAL_PROBABILITY = probability


def set_target_timing(target_timing):
    assert target_timing >= 0

    global TARGET_TIMING
    TARGET_TIMING = target_timing


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
        new_time = 0.7 * total_time + 0.3 * prev_time

        AVG_TIMINGS[key] = new_time


def should_assert(modpath, lineno, col_offset):
    key = (modpath, lineno, col_offset)
    duration = AVG_TIMINGS.get(key)

    if duration is None:
        return random.random() < INITIAL_PROBABILITY
    else:
        prob = TARGET_TIMING / duration

        return random.random() < prob
