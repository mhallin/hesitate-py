INITIAL_PROBABILITY = 1.0
TARGET_TIMING = 0.1
CONVERGENCE_FACTOR = 0.7


def set_initial_probability(probability):
    assert 0 <= probability <= 1

    global INITIAL_PROBABILITY
    INITIAL_PROBABILITY = probability


def set_target_timing(target_timing):
    assert target_timing >= 0

    global TARGET_TIMING
    TARGET_TIMING = target_timing


def set_convergence_factor(convergence_factor):
    assert 0 <= convergence_factor <= 1

    global CONVERGENCE_FACTOR
    CONVERGENCE_FACTOR = convergence_factor
