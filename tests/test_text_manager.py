import unittest
from texts import good_sentence_pairs, bad_sentence_pairs
from TextManager import TextManager


class TestTextManager(unittest.TestCase):
    def test_something(self):
        text_manager = TextManager(5, 0.7)

        for pair in good_sentence_pairs:
            similarity = text_manager.add_text(pair["sentence_1"])

        for pair in good_sentence_pairs:
            nearest, cosine_similarity = text_manager.get_max_similar(pair["sentence_2"])

            print(f"Found: {cosine_similarity}")

            self.assertEqual(nearest.data[0], pair["sentence_1"])


if __name__ == '__main__':
    unittest.main()
