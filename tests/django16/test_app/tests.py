from django.test import Client, TestCase


class RewriterTests(TestCase):
    def test_index_no_assert(self):
        c = Client()
        resp = c.get('/')

        self.assertEqual(resp.status_code, 200)
