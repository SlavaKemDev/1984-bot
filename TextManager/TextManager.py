import numpy as np

from QuadTree import QuadTree, Point
from DSU import DSU
from FastTextEmbedder import *
from .VertInfo import VertInfo

from datetime import datetime, timedelta


class TextManager:
    def __init__(self, max_neighbours, threshold, messages_time_gap: timedelta):
        self.max_neighbours = max_neighbours
        self.threshold = threshold
        self.messages_time_gap = messages_time_gap

        self.embedder = FastTextEmbedder()
        default_dim = self.embedder.get_embeddings("test").shape[0]

        self.quad_tree = QuadTree(Point([-1] * default_dim), Point([1] * default_dim))
        self.dsu = DSU()

    def add_text(self, text: str, dt: datetime):
        nearest, cosine_similarity = self.get_max_similar(text)
        if abs(cosine_similarity - 1) < 1e-4:
            dsu_vert = nearest.data[1]
            self.dsu.get_data(dsu_vert).set.add(dt)

            return

        embeddings = self.embedder.get_embeddings(text)
        norm = embeddings / np.linalg.norm(embeddings)

        dsu_vert = self.dsu.add_vertex(VertInfo(dt, False))

        self.quad_tree.add_point(Point(norm.tolist()), (text, dsu_vert))

    def get_max_similar(self, text: str):
        embeddings = self.embedder.get_embeddings(text)
        return self._get_max_similar(embeddings)

    def _get_max_similar(self, embeddings):
        if abs(np.linalg.norm(embeddings)) > 1e-7:
            norm = embeddings / np.linalg.norm(embeddings)
        else:
            return None, 0

        nearest = self.quad_tree.find_nearest(Point(norm.tolist()))

        if nearest is None:
            return None, 0

        nearest_norm = np.array(nearest.point.coords)

        cosine_similarity = FastTextEmbedder.cosine_similarity(norm, nearest_norm)

        return nearest, cosine_similarity

    def check_is_available(self, text: str, dt: datetime):
        nearest, cosine_similarity = self.get_max_similar(text)

        if nearest is None:
            return True

        print(nearest.data[0], cosine_similarity)

        dsu_vert = nearest.data[1]

        return (cosine_similarity < self.threshold
                or self.dsu.get_data(dsu_vert).can_merge_new(self.max_neighbours, self.messages_time_gap, dt))

    def mark_explicit(self, text):
        nearest, cosine_similarity = self._get_max_similar(self.embedder.get_embeddings(text))
        if cosine_similarity < self.threshold:
            self.add_text(text, datetime.now())
            nearest, cosine_similarity = self._get_max_similar(self.embedder.get_embeddings(text))

            assert cosine_similarity >= self.threshold

        dsu_vert = nearest.data[1]

        self.dsu.get_data(dsu_vert).is_banned = True
        assert self.dsu.get_data(dsu_vert).is_banned
