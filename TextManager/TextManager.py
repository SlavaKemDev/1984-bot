import numpy as np

from QuadTree import QuadTree, Point
from DSU import DSU
from BertEmbedder import BertEmbedder
from .VertInfo import VertInfo

from datetime import datetime, timedelta


class TextManager:
    def __init__(self, max_neighbours, threshold, messages_time_gap: timedelta):
        self.max_neighbours = max_neighbours
        self.threshold = threshold
        self.messages_time_gap = messages_time_gap

        self.embedder = BertEmbedder()
        default_dim = self.embedder.get_embeddings("test").shape[0]

        self.quad_tree = QuadTree(Point([0] * default_dim), Point([1] * default_dim))
        self.dsu = DSU()

    def add_text(self, text: str, dt: datetime):
        embeddings = self.embedder.get_embeddings(text)
        norm = embeddings / np.linalg.norm(embeddings)

        dsu_vert = self.dsu.add_vertex(VertInfo(dt, False))

        self.quad_tree.add_point(Point(norm.tolist()), (text, dsu_vert))

    def get_max_similar(self, text: str):
        embeddings = self.embedder.get_embeddings(text)
        return self._get_max_similar(embeddings)

    def _get_max_similar(self, embeddings):
        norm = embeddings / np.linalg.norm(embeddings)

        nearest = self.quad_tree.find_nearest(Point(norm.tolist()))
        nearest_norm = np.array(nearest.point.coords)

        cosine_similarity = BertEmbedder.cosine_similarity(norm, nearest_norm)

        return nearest, cosine_similarity

    def check_is_available(self, text: str, dt: datetime):
        embeddings = self.embedder.get_embeddings(text)
        nearest, cosine_similarity = self._get_max_similar(embeddings)

        dsu_vert = nearest.data[1]

        return (cosine_similarity < self.threshold
                or self.dsu.get_data(dsu_vert).can_merge_new(self.max_neighbours, self.messages_time_gap, dt))
