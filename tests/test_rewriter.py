from unittest import TestCase

from hesitate import attach_hook, set_initial_probability


class RewriterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        attach_hook()
        set_initial_probability(0.0)

    def test_plain_file(self):
        from . import impl_plain

        impl_plain.fn()

    def test_docstring_file(self):
        from . import impl_docstring

        impl_docstring.fn()

        self.assertEqual(impl_docstring.__doc__, 'Docstring')

    def test_futureimport_file(self):
        from . import impl_futureimport

        impl_futureimport.fn()
