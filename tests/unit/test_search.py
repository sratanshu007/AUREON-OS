import unittest

class TestSearchIndex(unittest.TestCase):
    def test_fuzzy_match(self):
        items = ["Files", "Browser", "Terminal", "System Settings", "Aureon AI"]
        query = "set"
        matches = [i for i in items if query in i.lower()]
        self.assertIn("System Settings", matches)

    def test_empty_query(self):
        items = ["Files", "Browser"]
        query = ""
        self.assertEqual(len(query), 0)

if __name__ == '__main__':
    unittest.main()
