import unittest
from BertEmbedder import BertEmbedder


class TestBertEmbedder(unittest.TestCase):
    def test_cosine_similarity(self):
        good_sentence_pairs = [
            {
                "sentence_1": "Вчера я посетил новый ресторан в центре города, и мне очень понравилась атмосфера.",
                "sentence_2": "На днях я побывал в новом кафе в центре города, и обстановка мне очень понравилась."
            },
            {
                "sentence_1": "Учёные провели исследование, которое подтвердило, что регулярные физические нагрузки улучшают общее состояние здоровья.",
                "sentence_2": "Исследование, проведённое учеными, показало, что занятия спортом способствуют улучшению здоровья."
            },
            {
                "sentence_1": "Новая книга популярного автора стала бестселлером и привлекла внимание множества читателей.",
                "sentence_2": "Недавняя публикация известного писателя быстро завоевала популярность и заинтересовала большое количество людей."
            },
            {
                "sentence_1": "Экологические проблемы, с которыми сталкивается наше общество, требуют немедленных действий и решений.",
                "sentence_2": "Существующие экологические вызовы, стоящие перед обществом, требуют срочных мер и решений."
            },
            {
                "sentence_1": "Многие люди считают, что чтение книг развивает мышление и улучшает память.",
                "sentence_2": "Существует мнение, что чтение литературы способствует развитию интеллекта и улучшению памяти."
            },
            {
                "sentence_1": "Путешествия обогащают наш опыт и позволяют нам лучше понимать другие культуры.",
                "sentence_2": "Поездки расширяют наши горизонты и помогают глубже узнать культуру других стран."
            }
        ]

        bad_sentence_pairs = [
            {
                "sentence_1": "Я люблю гулять по парку в солнечные дни.",
                "sentence_2": "Согласно последним новостям, в мире наблюдается экономический кризис."
            },
            {
                "sentence_1": "Моя кошка обожает спать на подоконнике.",
                "sentence_2": "В этом году мы планируем поехать в Европу на летний отпуск."
            },
            {
                "sentence_1": "Космические исследования помогают нам лучше понять Вселенную.",
                "sentence_2": "В нашем городе открывается новый супермаркет."
            },
            {
                "sentence_1": "Зимой снег покрывает улицы и делает город красивым.",
                "sentence_2": "Ведущие учёные мира обсуждают решения для борьбы с климатическими изменениями."
            },
            {
                "sentence_1": "Я предпочитаю кофе с молоком по утрам.",
                "sentence_2": "Спортивные соревнования часто привлекают множество зрителей."
            },
            {
                "sentence_1": "Старые здания в центре города напоминают о его богатой истории.",
                "sentence_2": "Новый телефон, который я купил, поддерживает 5G."
            }
        ]

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
