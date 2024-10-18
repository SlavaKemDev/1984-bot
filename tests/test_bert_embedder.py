import unittest
from BertEmbedder import BertEmbedder
from texts import good_sentence_pairs, bad_sentence_pairs


class TestBertEmbedder(unittest.TestCase):
    def test_cosine_similarity(self):
        embedder = BertEmbedder()

        good_answers = []
        bad_answers = []

        for pair in good_sentence_pairs:
            embeddings = embedder.get_embeddings([pair["sentence_1"], pair["sentence_2"]])
            similarity = embedder.cosine_similarity(embeddings[0], embeddings[1])
            good_answers.append(similarity)

        for pair in bad_sentence_pairs:
            embeddings = embedder.get_embeddings([pair["sentence_1"], pair["sentence_2"]])
            similarity = embedder.cosine_similarity(embeddings[0], embeddings[1])
            bad_answers.append(similarity)

        good_mean = sum(good_answers) / len(good_answers)
        bad_mean = sum(bad_answers) / len(bad_answers)

        print("Good cos similarity:", good_mean)
        print("Bad cos similarity:", bad_mean)

        self.assertGreater(good_mean, bad_mean)


if __name__ == '__main__':
    unittest.main()
