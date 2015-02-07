from unittest import TestSuite, TestLoader

from .test_rewriter import RewriterTest


def all_tests():
    suite = TestSuite()
    loader = TestLoader()

    suite.addTests(loader.loadTestsFromTestCase(RewriterTest))

    return suite
